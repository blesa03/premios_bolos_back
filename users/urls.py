from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, UserListView, LoginView

urlpatterns = [
    path("login/", LoginView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("list/", UserListView.as_view(), name="user_list"),
]