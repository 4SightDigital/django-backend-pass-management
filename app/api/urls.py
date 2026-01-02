from django.urls import path
from .views import (
    VenueListCreateAPI,
    VenueDetailAPI,
    VenueSpaceTreeAPI,
    EventListCreateAPI,
    EventDetailAPI,
    UserListAPI,
    AllocationListAPI,
    MetaEnumsAPI,
)

urlpatterns = [

    # Venues
    path('venues/', VenueListCreateAPI.as_view()),
    path('venues/<int:pk>/', VenueDetailAPI.as_view()),
    path('venues/<int:venue_id>/space-tree/', VenueSpaceTreeAPI.as_view()),

    # Events
    path('events/', EventListCreateAPI.as_view()),
    path('events/<int:pk>/', EventDetailAPI.as_view()),

    # Users
    path('users/', UserListAPI.as_view()),

    # Allocations
    path('allocations/', AllocationListAPI.as_view()),

    # Meta
    path('meta/enums/', MetaEnumsAPI.as_view()),
]
