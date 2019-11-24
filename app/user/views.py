from rest_framework import generics,  permissions
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from .serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Creates a new user in the system"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user
