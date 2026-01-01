from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404

from app.models import (
    Venue,
    SpaceCategory,
    Event,
    CustomUser,
    SpaceAllocation,
)
from .serializers import (
    VenueSerializer,
    EventSerializer,
    UserSerializer,
    AllocationSerializer,
    SpaceCategorySerializer,
)
from app.views import calculate_seats_with_children, create_recursive


# ================= VENUE =================
class VenueListCreateAPI(generics.ListCreateAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_permissions(self):
        return [AllowAny()]


class VenueDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_permissions(self):
        return [AllowAny()]


# ================= VENUE HIERARCHY =================
class VenueHierarchyAPI(generics.GenericAPIView):
    serializer_class = SpaceCategorySerializer

    def get_permissions(self):
        return [AllowAny()]

    def get(self, request, venue_id):
        categories = SpaceCategory.objects.filter(
            venue_id=venue_id,
            parent=None
        )
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data)

    @transaction.atomic
    def post(self, request, venue_id):
        venue = get_object_or_404(Venue, id=venue_id)

        # 1. Extract seating array from frontend payload
        seating = request.data.get("seating", [])
        if not isinstance(seating, list):
            return Response(
                {"error": "Invalid seating format"},
                status=400
            )

        # 2. Normalize frontend structure → backend structure
        def normalize_category(category):
            return {
                "name": category.get("categoryName") or category.get("name"),
                "seats_count": category.get("categoryTotalSeats") or category.get("seats"),
                "children": [
                    normalize_category(child)
                    for child in category.get("subCategories", [])
                ]
            }

        hierarchy = [normalize_category(cat) for cat in seating]

        # 3. Validate total seats against venue capacity
        total_seats = calculate_seats_with_children(hierarchy)
        if total_seats > venue.total_capacity:
            return Response(
                {"error": "Total seats exceed venue capacity"},
                status=400
            )

        # 4. Replace existing hierarchy
        venue.spaces.all().delete()
        create_recursive(hierarchy, venue)

        return Response(
            {"status": "Hierarchy saved successfully"},
            status=200
        )


# ================= EVENT =================
class EventListCreateAPI(generics.ListCreateAPIView):
    queryset = Event.objects.select_related('venue')
    serializer_class = EventSerializer

    def get_permissions(self):
        return [AllowAny()]


class EventDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        return [AllowAny()]


# ================= USER =================
class UserListAPI(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# ================= ALLOCATION =================
class AllocationListAPI(generics.ListCreateAPIView):
    queryset = SpaceAllocation.objects.select_related(
        'event', 'category', 'source'
    )
    serializer_class = AllocationSerializer

    def get_permissions(self):
        return [AllowAny()]
