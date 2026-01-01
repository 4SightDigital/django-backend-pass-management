from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
import json

from .forms import VenueForm, CustomUserForm, EventForm, AllocationSourceForm
from .models import Venue, SpaceCategory, CustomUser, Event, AllocationSource, SpaceAllocation   

# ---------------------------
# LOGIN / DASHBOARD
# ---------------------------
class CustomLoginView(LoginView):
    template_name = 'login.html'


@login_required
def base_view(request):
    return render(request, 'base.html')


@login_required
def dashboard_view(request):
    # Fetch all events so we can show them as cards on the main dashboard
    events = Event.objects.all().select_related('venue').order_by('-start_datetime')
    
    # Optional: Calculate some quick stats for the top cards
    stats = {
        'total_events': events.count(),
        'total_venues': Venue.objects.count(),
        'total_allocations': SpaceAllocation.objects.count(),
    }
    
    return render(request, 'dashboard.html', {
        'events': events,
        'stats': stats
    })

# ---------------------------
# VENUES
# ---------------------------
# Recursive function to calculate total seats including all children
def calculate_seats_with_children(items):
    total = 0
    for item in items:
        children = item.get('children', [])
        # Recursively calculate seats for children
        children_total = calculate_seats_with_children(children)
        # Parent seats = own seats + children_total
        item['seats'] = (item.get('seats') or 0) + children_total
        total += item['seats']
    return total

# Recursive function to create SpaceCategory objects
def create_recursive(items, venue, parent_obj=None):
    for item in items:
        category = SpaceCategory.objects.create(
            venue=venue,
            parent=parent_obj,
            name=item['name'],
            category_type=item.get('type', ''),
            seats_count=item.get('seats') or 0
        )
        if item.get('children'):
            create_recursive(item['children'], venue, parent_obj=category)

@transaction.atomic
@login_required
def venues_page(request):
    venues = Venue.objects.all().prefetch_related('spaces')

    if request.method == "POST" and 'add_venue' in request.POST:
        venue_form = VenueForm(request.POST)
        if venue_form.is_valid():
            venue = venue_form.save()
            json_data = request.POST.get('hierarchy_json')
            if json_data:
                try:
                    hierarchy = json.loads(json_data)
                    # Aggregate seats including subcategories
                    total_seats = calculate_seats_with_children(hierarchy)

                    if total_seats > venue.total_capacity:
                        messages.error(request, f"Total seats ({total_seats}) exceed venue capacity ({venue.total_capacity})!")
                        venue.delete()
                        return redirect('venues_page')

                    # Create categories recursively
                    create_recursive(hierarchy, venue)

                except Exception as e:
                    messages.error(request, f"Layout error: {str(e)}")
            messages.success(request, f"Venue '{venue.name}' created.")
            return redirect('venues_page')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        venue_form = VenueForm()

    return render(request, 'venues.html', {
        'venue_form': venue_form,
        'venues': venues
    })

@transaction.atomic
@login_required
def save_hierarchy(request, venue_id):
    if request.method == "POST":
        venue = get_object_or_404(Venue, id=venue_id)
        json_data = request.POST.get('hierarchy_json')
        try:
            hierarchy = json.loads(json_data) if json_data else []

            # Aggregate seats including subcategories
            total_seats = calculate_seats_with_children(hierarchy)
            if total_seats > venue.total_capacity:
                messages.error(request, f"Total seats ({total_seats}) exceed venue capacity ({venue.total_capacity})!")
                return redirect('venues_page')

            # Delete old categories and recreate hierarchy
            venue.spaces.all().delete()
            create_recursive(hierarchy, venue)
            messages.success(request, "Venue layout updated.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    return redirect('venues_page')

@login_required
def get_hierarchy_json(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)

    def recursive_fetch(categories):
        return [{
            "name": cat.name,
            "type": cat.category_type,
            "seats": cat.seats_count,
            "children": recursive_fetch(cat.children.all())
        } for cat in categories]

    # Fetching only root categories (those with no parent)
    root_cats = venue.spaces.filter(parent=None)
    return JsonResponse(recursive_fetch(root_cats), safe=False)
@login_required
def edit_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    if request.method == "POST":
        form = VenueForm(request.POST, instance=venue)
        if form.is_valid():
            form.save()
            messages.success(request, "Venue details updated.")
            return redirect('venues_page')
    else:
        form = VenueForm(instance=venue)
    return render(request, 'venues.html', {
        'venue_form': form,
        'venues': Venue.objects.all(),
        'edit_venue': venue
    })

@login_required
def delete_venue(request, venue_id):
    venue = get_object_or_404(Venue, id=venue_id)
    if request.method == "POST":
        venue.delete()
        messages.success(request, "Venue deleted.")
    return redirect('venues_page')


# ---------------------------
# USERS
# ---------------------------
@login_required
def users_page(request):
    if not (request.user.is_superuser or request.user.access_rights == 'SuperAdmin'):
        messages.error(request, "Permission denied.")
        return redirect('dashboard_view')

    users = CustomUser.objects.all().order_by('-date_joined')
    form = CustomUserForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        new_user = form.save(commit=False)
        new_user.set_password('adminpassword')
        new_user.is_staff = True
        new_user.save()
        messages.success(request, f"User '{new_user.username}' created!")
        return redirect('users_page')

    return render(request, 'users.html', {'users': users, 'form': form})


@require_POST
@login_required
def update_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.username = request.POST.get('username')
    user.first_name = request.POST.get('first_name')
    user.last_name = request.POST.get('last_name')
    user.email = request.POST.get('email')

    new_rights = request.POST.get('access_rights')
    if new_rights:
        user.access_rights = new_rights

    user.save()
    return JsonResponse({
        'success': True,
        'username': user.username,
        'full_name': user.get_full_name(),
        'email': user.email,
        'access_rights': user.get_access_rights_display()
    })


@require_POST
@login_required
def delete_user(request, user_id):
    if not (request.user.is_superuser or request.user.access_rights == 'SuperAdmin'):
        messages.error(request, "You do not have permission to perform this action.")
        return redirect('users_page')

    user_to_delete = get_object_or_404(CustomUser, id=user_id)
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('users_page')

    username = user_to_delete.username
    user_to_delete.delete()
    messages.success(request, f"User '{username}' has been deleted.")
    return redirect('users_page')


# ---------------------------
# CHANGE PASSWORD
# ---------------------------
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was changed successfully.')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'change_password.html', {'form': form})


# ---------------------------
# EVENTS
# ---------------------------
@login_required
def events_page(request):
    events = Event.objects.all().order_by('-start_datetime')
    form = EventForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        venue = form.cleaned_data['venue']
        start = form.cleaned_data['start_datetime']
        end = form.cleaned_data['end_datetime']

        overlapping = Event.objects.filter(
            venue=venue,
            start_datetime__lt=end,
            end_datetime__gt=start
        ).exists()

        if overlapping:
            messages.error(request, f"Conflict: {venue.name} is already booked.")
        else:
            form.save()
            messages.success(request, "Event created successfully!")
            return redirect('events_page')

    return render(request, 'events.html', {'form': form, 'events': events})


@login_required
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    events = Event.objects.all().order_by('-start_datetime')
    form = EventForm(request.POST or None, instance=event)

    if request.method == "POST" and form.is_valid():
        venue = form.cleaned_data['venue']
        start = form.cleaned_data['start_datetime']
        end = form.cleaned_data['end_datetime']

        overlapping = Event.objects.filter(
            venue=venue,
            start_datetime__lt=end,
            end_datetime__gt=start
        ).exclude(id=event.id).exists()

        if overlapping:
            messages.error(request, "Conflict: Venue is already booked for this time.")
        else:
            form.save()
            messages.success(request, "Event updated successfully!")
            return redirect('events_page')

    return render(request, 'events.html', {
        'form': form,
        'events': events,
        'edit_mode': True,
        'event_instance': event
    })


@login_required
@require_POST
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    messages.success(request, "Event deleted successfully.")
    return redirect('events_page')


# ---------------------------
# ALLOCATION SOURCES
# ---------------------------
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
import json

from .models import Event, Venue, SpaceCategory, AllocationSource, SpaceAllocation
from .forms import AllocationSourceForm

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
import json
from .models import Event, SpaceCategory, AllocationSource, SpaceAllocation
from .forms import AllocationSourceForm
from django.db.models import Sum
from django.db.models import Model, ForeignKey, Sum  # Example
@login_required
def allocation_sources_page(request):
    # Fetch all allocations
    allocations = SpaceAllocation.objects.select_related(
        'event', 'source', 'category', 'category__venue'
    ).order_by('-created_at')

    # Calculate "Zone Remaining" for each allocation row
    for alloc in allocations:
        # Sum up every allocation made for this specific Event and Category
        total_allocated_in_zone = SpaceAllocation.objects.filter(
            event=alloc.event,
            category=alloc.category
        ).aggregate(total=Sum('total_quantity'))['total'] or 0
        
        # Available in Zone = Total Seats - Sum of all Allocations
        alloc.zone_remaining = alloc.category.seats_count - total_allocated_in_zone

    events = Event.objects.select_related('venue').all()
    categories = SpaceCategory.objects.select_related('venue').all()
    form = AllocationSourceForm(request.POST or None)

    if request.method == "POST":
        event_id = request.POST.get('event')
        source_name = request.POST.get('source_name')
        category_id = request.POST.get('ticket_category')
        quantity = request.POST.get('tickets_available')

        if all([event_id, source_name, category_id, quantity]):
            event = get_object_or_404(Event, id=event_id)
            category = get_object_or_404(SpaceCategory, id=category_id)
            
            # Logic to check if the new allocation exceeds zone capacity
            allocated_total = SpaceAllocation.objects.filter(
                event=event, category=category
            ).aggregate(total=Sum('total_quantity'))['total'] or 0
            
            available_seats = category.seats_count - allocated_total

            if int(quantity) > available_seats:
                messages.error(request, f"Insufficient seats. Only {available_seats} left in {category.name}.")
            else:
                source, _ = AllocationSource.objects.get_or_create(
                    name=source_name.strip(),
                    event=event,
                    venue=category.venue,
                    ticket_category=category
                )
                SpaceAllocation.objects.create(
                    event=event,
                    source=source,
                    category=category,
                    total_quantity=int(quantity),
                    referral_token=f"REF-{event.id}-{category.id}-{timezone.now().timestamp()}"
                )
                messages.success(request, f"Allocated {quantity} seats to '{source_name}'.")
                return redirect('allocation_sources_page')

    categories_json = json.dumps({
        c.id: {'seats': c.seats_count, 'venue_id': c.venue.id, 'name': c.name}
        for c in categories
    })

    context = {
        'allocations': allocations,
        'form': form,
        'events': events,
        'categories': categories,
        'categories_json': categories_json,
    }
    return render(request, 'allocation_sources.html', context)





from django.db.models import Sum, F
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.utils import timezone
from .models import Event, SpaceCategory, SpaceAllocation, Claim, AllocationSource

@login_required
def event_dashboard(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    # Fetch available allocation sources for this event to populate the dropdown
    sources = AllocationSource.objects.filter(event=event)
    
    categories = SpaceCategory.objects.filter(venue=event.venue).prefetch_related('children')
    
    dashboard_data = []
    for cat in categories:
        total = cat.seats_count
        # Total currently allocated across all sources for this category
        allocated = SpaceAllocation.objects.filter(
            event=event, category=cat
        ).aggregate(res=Sum('total_quantity'))['res'] or 0
        
        # Remaining overall for the venue category
        available = total - allocated

        dashboard_data.append({
            'category': cat,
            'total': total,
            'allocated': allocated,
            'available': available,
            'is_parent': cat.parent is None
        })

    return render(request, 'dashboard_event_grid.html', {
        'event': event,
        'dashboard_data': dashboard_data,
        'sources': sources,  
    })

@require_POST
@login_required
def process_claim(request):
    event_id = request.POST.get('event_id')
    category_id = request.POST.get('category_id')
    source_id = request.POST.get('source_id')  # New: Get selected Source
    qty_str = request.POST.get('quantity')
    name = request.POST.get('claimant_name')
    dept = request.POST.get('department', '')

    if not all([category_id, source_id, qty_str, name]):
        messages.error(request, "Please select a source, category, and fill in all fields.")
        return redirect('event_dashboard', event_id=event_id)

    qty = int(qty_str)
    
    # Find the specific allocation for this Category AND Source
    allocation = SpaceAllocation.objects.filter(
        event_id=event_id, 
        category_id=category_id,
        source_id=source_id
    ).first()
    
    if not allocation:
        messages.error(request, "This Source does not have an allocation for the selected Category.")
    elif qty > allocation.remaining_quantity:
        messages.error(request, f"Insufficient seats! This source only has {allocation.remaining_quantity} left.")
    else:
        # Create the claim linked to the specific source allocation
        Claim.objects.create(
            allocation=allocation,
            claimant_name=name,
            department=dept,
            quantity=qty
        )
        messages.success(request, f"Successfully booked {qty} seats for {name} (Source: {allocation.source.name}).")

    return redirect('event_dashboard', event_id=event_id)