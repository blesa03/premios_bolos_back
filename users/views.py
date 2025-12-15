from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import User
from .serializers import UserProfileSerializer, UserListSerializer, LoginSerializer


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
    
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]

class LoginView(TokenObtainPairView):
    """
    Vista de login JWT personalizada:
    - Permite acceso sin autenticación
    - Usa LoginSerializer para añadir info del usuario
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]