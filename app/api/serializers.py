from rest_framework import serializers
from app.models import (
    Venue,
    SpaceCategory,
    Event,
    CustomUser,
    SpaceAllocation,
)

# =====================================================
# SPACE CATEGORY (TREE, DEV FRIENDLY)
# =====================================================

class SpaceCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    is_leaf = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = SpaceCategory
        fields = [
            'id',
            'venue',
            'parent',

            # Meaningful fields
            'name',            # Example: VVIP / Block A
            'category_type',   # Tier / Block / Section
            'ticket_tier',     # VVIP / VIP / Regular
            'seats_count',

            # Helper fields
            'is_leaf',
            'display_name',
            'children',
        ]

    def get_children(self, obj):
        return SpaceCategorySerializer(
            obj.children.all(),
            many=True
        ).data

    def get_is_leaf(self, obj):
        return not obj.children.exists()

    def get_display_name(self, obj):
        """
        Examples:
        - VVIP
        - VVIP → Block A
        """
        if obj.parent:
            return f"{obj.parent.name} → {obj.name}"
        return obj.name


# =====================================================
# VENUE
# =====================================================

class VenueSerializer(serializers.ModelSerializer):
    space_tree = serializers.SerializerMethodField()

    class Meta:
        model = Venue
        fields = [
            'id',
            'name',
            'address',
            'location',
            'venue_type',
            'total_capacity',
            'space_tree',
        ]

    def get_space_tree(self, obj):
        roots = obj.spaces.filter(parent=None)
        return SpaceCategorySerializer(roots, many=True).data


# =====================================================
# EVENT
# =====================================================

class EventSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(source='venue.name', read_only=True)

    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'venue',
            'venue_name',
            'start_datetime',
            'end_datetime',
        ]


# =====================================================
# USER
# =====================================================

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'access_rights',
        ]


# =====================================================
# SPACE ALLOCATION
# =====================================================

class AllocationSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    venue_name = serializers.CharField(source='event.venue.name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)

    category = serializers.SerializerMethodField()

    class Meta:
        model = SpaceAllocation
        fields = [
            'id',

            # Event info
            'event',
            'event_name',
            'venue_name',

            # Category info
            'category',

            # Allocation info
            'source_name',
            'total_quantity',
            'remaining_quantity',

            # Meta
            'referral_token',
            'created_at',
        ]

    def get_category(self, obj):
        return {
            "id": obj.category.id,
            "name": obj.category.name,
            "ticket_tier": obj.category.ticket_tier,
            "display_name": (
                f"{obj.category.parent.name} → {obj.category.name}"
                if obj.category.parent else obj.category.name
            )
        }
