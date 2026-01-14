from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.api.serializers.auth_serializer import RegisterSerializer, UserSerializer

User = get_user_model()

@extend_schema(
    summary="Register a new user",
    description="Creates a new user account and an initial associated account (e.g. MoMo).",
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
    examples=[
        OpenApiExample(
            'Register Example',
            value={
                'phone_number': '677123456',
                'password': 'securepassword',
                'first_name': 'John',
                'initial_amount': 5000
            },
            request_only=True
        )
    ]
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

@extend_schema(
    summary="Obtain JWT Token",
    description="Takes phone number and password, returns access and refresh tokens."
)
class CustomTokenObtainPairView(TokenObtainPairView):
    # Depending on needs, we could customize the token here
    pass

@extend_schema(tags=['auth'])
class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user
