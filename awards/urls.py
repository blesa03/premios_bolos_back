from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    AwardListView,
    AwardDetailView,
    AwardNominationsListView,
    AwardSuggestionListCreateView,
    AwardResultsView,
    AwardVoteView,
)

urlpatterns = [
    path("list/", AwardListView.as_view(), name="award-list"),
    path("<int:pk>/", AwardDetailView.as_view(), name="award-detail"),
    path("<int:award_id>/nominations/", AwardNominationsListView.as_view(), name="award-nominations"),
    path("suggestions/", AwardSuggestionListCreateView.as_view(), name="award-suggestions"),
    path("<int:award_id>/results/", AwardResultsView.as_view(), name="award-results"),
    path("<int:award_id>/vote/", AwardVoteView.as_view(), name="award-vote"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)