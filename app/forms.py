from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Venue, SpaceCategory, CustomUser, Event, AllocationSource

# ---------------------------
# VENUE FORM
# ---------------------------
class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'location', 'venue_type', 'total_capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Venue Name'}),
            'location': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Address...'}),
            'venue_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Stadium'}),
            'total_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# ---------------------------
# SPACE CATEGORY FORM
# ---------------------------
from django import forms
from .models import SpaceCategory

class SpaceCategoryForm(forms.ModelForm):
    class Meta:
        model = SpaceCategory
        fields = ['venue', 'name', 'seats_count']  # only actual fields
        widgets = {
            'venue': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
            'seats_count': forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        }

# ---------------------------
# CUSTOM USER FORM
# ---------------------------
class CustomUserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'access_rights']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'access_rights': forms.Select(attrs={'class': 'form-control'}),
        }

# ---------------------------
# EVENT FORM
# ---------------------------
class EventForm(forms.ModelForm):
    start_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="Start Date & Time"
    )
    end_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        label="End Date & Time"
    )

    class Meta:
        model = Event
        fields = ['venue', 'name', 'start_datetime', 'end_datetime']
        widgets = {
            'venue': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Name'}),
        }

# ---------------------------
# ALLOCATION SOURCE FORM
# ---------------------------
from django import forms
from .models import AllocationSource, Event, SpaceCategory

class AllocationSourceForm(forms.ModelForm):
    # Manual field for the quantity since it might differ from the model field name in your HTML
    tickets_available = forms.IntegerField(min_value=1, label="Tickets to Allocate")
    referral_token = forms.CharField(required=False)

    class Meta:
        model = AllocationSource
        fields = ['event', 'ticket_category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update classes for Bootstrap styling
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Ensure categories show venue names for clarity
        self.fields['ticket_category'].queryset = SpaceCategory.objects.select_related('venue').all()