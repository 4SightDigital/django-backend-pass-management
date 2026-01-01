from rest_framework import serializers
from app.models import (
    Venue,
    SpaceCategory,
    Event,
    CustomUser,
    SpaceAllocation,
)

# ================= SPACE CATEGORY =================
class SpaceCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = SpaceCategory
        fields = [
            'id',
            'venue',
            'parent',
            'name',
            'category_type',
            'ticket_tier',
            'seats_count',
            'children',
        ]

    def get_children(self, obj):
        return SpaceCategorySerializer(
            obj.children.all(),
            many=True
        ).data


# ================= VENUE =================
class VenueSerializer(serializers.ModelSerializer):
    spaces = SpaceCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Venue
        fields = '__all__'


# ================= EVENT =================
class EventSerializer(serializers.ModelSerializer):
    venue_name = serializers.CharField(
        source="venue.name",
        read_only=True
    )

    start_datetime = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M"
    )
    end_datetime = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M"
    )

    class Meta:
        model = Event
        fields = "__all__"


# ================= USER =================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'access_rights']


# ================= ALLOCATION =================
class AllocationSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)

    class Meta:
        model = SpaceAllocation
        fields = '__all__'
