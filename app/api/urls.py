from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from app.views import (
    CustomLoginView,
    base_view,
    dashboard_view,
    users_page,
    update_user,
    delete_user,
    change_password,
    venues_page,
    save_hierarchy,
    edit_venue,
    delete_venue,
    get_hierarchy_json,
    events_page,
    edit_event,
    delete_event
)
from app.views import allocation_sources_page
from django.urls import path
from . import views  # The dot (.) tells Python to look in the current folder
urlpatterns = [
    # Dashboard / Home
    path('', login_required(base_view), name='base'),
    path('dashboard/', login_required(dashboard_view), name='dashboard_view'),

    # Auth
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('change-password/', login_required(change_password), name='change_password'),

    # Users
    path('users/', login_required(users_page), name='users_page'),  # unified users page
    path('users/update/<int:user_id>/', login_required(update_user), name='update_user'),
    path('users/delete/<int:user_id>/', login_required(delete_user), name='delete_user'),

    # Venues
    path('venues/', views.venues_page, name='venues_page'),
    path('venues/delete/<int:venue_id>/', views.delete_venue, name='delete_venue'),
    path('venues/<int:venue_id>/hierarchy/', views.get_hierarchy_json, name='get_hierarchy_json'),
    path('venues/save-hierarchy/<int:venue_id>/', views.save_hierarchy, name='save_hierarchy'),
    path('allocation-sources/', views.allocation_sources_page, name='allocation_sources_page'),

    # Events
    path('events/', login_required(events_page), name='events_page'),
    path('events/edit/<int:event_id>/', login_required(edit_event), name='edit_event'),
    path('events/delete/<int:event_id>/', login_required(delete_event), name='delete_event'),
    path('allocation-sources/', login_required(allocation_sources_page), name='allocation_sources_page'),
    
    
    # Event-specific Excel-style Dashboard
    path('event-dashboard/<int:event_id>/', views.event_dashboard, name='event_dashboard'),
    
    # Action to process the booking/claim
    path('process-claim/', views.process_claim, name='process_claim'),

]
