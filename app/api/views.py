from rest_framework import generics
from rest_framework.permissions import AllowAny, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
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

# =====================================================
# HELPER FUNCTIONS (MUST BE ABOVE THE VIEWS)
# =====================================================

def calculate_seats_with_children(hierarchy):
    total = 0
    for node in hierarchy:
        total += node.get("seats_count", 0)

        children = node.get("children", [])
        if children:
            total += calculate_seats_with_children(children)

    return total


def create_recursive(hierarchy, venue, parent=None):
    for node in hierarchy:
        category = SpaceCategory.objects.create(
            venue=venue,
            parent=parent,
            name=node["name"],
            category_type=node["category_type"],
            ticket_tier=node.get("ticket_tier"),
            seats_count=node.get("seats_count", 0),
        )

        children = node.get("children", [])
        if children:
            create_recursive(children, venue, category)

# =====================================================
# VENUES
# =====================================================

class VenueListCreateAPI(generics.ListCreateAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()]


class VenueDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()]


# =====================================================
# SPACE CATEGORY TREE
# =====================================================

class VenueSpaceTreeAPI(generics.GenericAPIView):
    serializer_class = SpaceCategorySerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
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
        hierarchy = request.data

        total_seats = calculate_seats_with_children(hierarchy)
        if total_seats > venue.total_capacity:
            return Response(
                {"error": "Total seats exceed venue capacity"},
                status=400
            )

        venue.spaces.all().delete()
        create_recursive(hierarchy, venue)

        return Response({"status": "Space hierarchy saved successfully"})

# =====================================================
# EVENTS
# =====================================================

class EventListCreateAPI(generics.ListCreateAPIView):
    queryset = Event.objects.select_related('venue')
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()]


class EventDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()]


# =====================================================
# USERS
# =====================================================

class UserListAPI(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# =====================================================
# ALLOCATIONS
# =====================================================

class AllocationListAPI(generics.ListCreateAPIView):
    queryset = SpaceAllocation.objects.select_related(
        'event', 'category', 'source'
    )
    serializer_class = AllocationSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [AllowAny()]


# =====================================================
# META / ENUMS
# =====================================================

class MetaEnumsAPI(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({
            "category_types": ["Tier", "Block", "Section"],
            "ticket_tiers": ["VVIP", "VIP", "Regular"],
            "rules": {
                "seats_exist_only_on_leaf_nodes": True,
                "parent_seats_should_be_zero": True
            }
        })
