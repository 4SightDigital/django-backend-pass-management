from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.core.exceptions import ValidationError

# -----------------------------
# Custom User
# -----------------------------
ROLE_CHOICES = (
    ('SuperAdmin', 'SuperAdmin'),
    ('EventAdmin', 'EventAdmin'),
    ('GateStaff', 'GateStaff'),
)

class CustomUser(AbstractUser):
    access_rights = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='GateStaff',
        verbose_name='Access Rights'
    )
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_set_permissions',
        blank=True
    )

    class Meta:
        verbose_name = "Custom User"

# -----------------------------
# Venue
# -----------------------------
class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    location = models.TextField(blank=True)  # Optional GPS/location info
    venue_type = models.CharField(max_length=100)  # Indoor/Outdoor/Hybrid
    total_capacity = models.PositiveIntegerField()  # Total number of seats

    def __str__(self):
        return f"{self.name} (Capacity: {self.total_capacity})"

# -----------------------------
# SpaceCategory
# -----------------------------
class SpaceCategory(models.Model):
    venue = models.ForeignKey(Venue, related_name='spaces', on_delete=models.CASCADE)
    # ADD THESE TWO FIELDS:
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    category_type = models.CharField(max_length=100, blank=True) 
    
    name = models.CharField(max_length=255)
    ticket_tier = models.CharField(max_length=100, blank=True)
    seats_count = models.PositiveIntegerField()

    class Meta:
        unique_together = ('venue', 'name')

    def __str__(self):
        return f"{self.venue.name} - {self.name} ({self.seats_count} seats)"

    def clean(self):
        # Validation to ensure we don't exceed venue capacity
        total_allocated = sum([c.seats_count for c in self.venue.spaces.exclude(id=self.id)])
        if total_allocated + self.seats_count > self.venue.total_capacity:
            raise ValidationError(f"Exceeds venue capacity of {self.venue.total_capacity}")
# -----------------------------
# Event
# -----------------------------
class Event(models.Model):
    name = models.CharField(max_length=255)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.name} ({self.venue.name})"

# -----------------------------
# AllocationSource
# -----------------------------
class AllocationSource(models.Model):
    name = models.CharField(max_length=255)  # Person/organization distributing tickets
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='allocations')
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    ticket_category = models.ForeignKey(SpaceCategory, on_delete=models.CASCADE)
    tickets_allocated = models.PositiveIntegerField(default=0)  # Seats allocated to this source
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.tickets_allocated} seats - {self.ticket_category.name} - {self.event.name})"

    def clean(self):
        # Ensure category belongs to venue
        if self.ticket_category.venue != self.venue:
            raise ValidationError("Ticket category does not belong to selected venue.")

        # Ensure tickets_allocated does not exceed available seats
        allocated_seats = sum([
            alloc.tickets_allocated
            for alloc in AllocationSource.objects.filter(
                event=self.event,
                ticket_category=self.ticket_category
            ).exclude(id=self.id)
        ])
        available_seats = self.ticket_category.seats_count - allocated_seats
        if self.tickets_allocated > available_seats:
            raise ValidationError(
                f"Cannot allocate {self.tickets_allocated} tickets. Only {available_seats} seats left in {self.ticket_category.name}."
            )

# -----------------------------
# SpaceAllocation
# -----------------------------
class SpaceAllocation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    source = models.ForeignKey(AllocationSource, on_delete=models.CASCADE)
    category = models.ForeignKey(SpaceCategory, on_delete=models.CASCADE)
    total_quantity = models.PositiveIntegerField()
    remaining_quantity = models.PositiveIntegerField(blank=True, null=True)
    referral_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(default=timezone.now)

    def update_remaining(self):
        """Calculates and saves the remaining seats based on Claims."""
        # Sum of all quantities in Claim objects linked to this allocation
        total_claimed = self.claims.aggregate(total=models.Sum('quantity'))['total'] or 0
        self.remaining_quantity = self.total_quantity - total_claimed
        self.save()

    def save(self, *args, **kwargs):
        if self.remaining_quantity is None:
            self.remaining_quantity = self.total_quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.source.name} - {self.category.name}"

# -----------------------------
# Claim
# -----------------------------
# --- Ensure Claim model looks like this ---
class Claim(models.Model):
    allocation = models.ForeignKey(SpaceAllocation, related_name='claims', on_delete=models.CASCADE)
    claimant_name = models.CharField(max_length=255)
    # Add department if you want to store it from the form
    department = models.CharField(max_length=255, blank=True, null=True) 
    quantity = models.PositiveIntegerField()
    claimed_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # This now works because we added the method above!
        self.allocation.update_remaining()






