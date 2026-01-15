import logging
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.api.serializers.auth_serializer import RegisterSerializer, UserSerializer

logger = logging.getLogger(__name__)
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
    
    def create(self, request, *args, **kwargs):
        logger.info(f"[REGISTER] Registration attempt started")
        logger.debug(f"[REGISTER] Request data: {request.data}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"[REGISTER] Validation failed: {serializer.errors}")
                logger.debug(f"[REGISTER] Invalid data: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"[REGISTER] Validation successful, creating user")
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            logger.info(f"[REGISTER] User created successfully: {serializer.data.get('phone_number')}")
            logger.debug(f"[REGISTER] Created user data: {serializer.data}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            logger.error(f"[REGISTER] Registration failed with exception: {str(e)}", exc_info=True)
            logger.error(f"[REGISTER] Request data that caused error: {request.data}")
            return Response(
                {"error": "Registration failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema(
    summary="Obtain JWT Token",
    description="Takes phone number and password, returns access and refresh tokens."
)
class CustomTokenObtainPairView(TokenObtainPairView):
    
    def post(self, request, *args, **kwargs):
        logger.info(f"[LOGIN] Login attempt started")
        logger.debug(f"[LOGIN] Login attempt for user: {request.data.get('phone_number', 'N/A')}")
        
        try:
            response = super().post(request, *args, **kwargs)
            
            if response.status_code == 200:
                logger.info(f"[LOGIN] Login successful for user: {request.data.get('phone_number', 'N/A')}")
                logger.debug(f"[LOGIN] Tokens generated successfully")
            else:
                logger.warning(f"[LOGIN] Login failed for user: {request.data.get('phone_number', 'N/A')}")
                logger.debug(f"[LOGIN] Response status: {response.status_code}, data: {response.data}")
            
            return response
            
        except Exception as e:
            logger.error(f"[LOGIN] Login failed with exception: {str(e)}", exc_info=True)
            logger.error(f"[LOGIN] User attempted: {request.data.get('phone_number', 'N/A')}")
            raise

@extend_schema(tags=['auth'])
class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    
    def get_object(self):
        logger.debug(f"[USER_DETAIL] Retrieving user object for: {self.request.user}")
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"[USER_DETAIL] User detail retrieval for: {request.user}")
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.debug(f"[USER_DETAIL] User data retrieved: {serializer.data}")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"[USER_DETAIL] Failed to retrieve user detail: {str(e)}", exc_info=True)
            logger.error(f"[USER_DETAIL] User: {request.user}")
            raise
    
    def update(self, request, *args, **kwargs):
        logger.info(f"[USER_UPDATE] User update attempt for: {request.user}")
        logger.debug(f"[USER_UPDATE] Update data: {request.data}")
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if not serializer.is_valid():
                logger.warning(f"[USER_UPDATE] Validation failed: {serializer.errors}")
                logger.debug(f"[USER_UPDATE] Invalid data: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            logger.info(f"[USER_UPDATE] User updated successfully: {request.user}")
            logger.debug(f"[USER_UPDATE] Updated data: {serializer.data}")
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"[USER_UPDATE] Update failed with exception: {str(e)}", exc_info=True)
            logger.error(f"[USER_UPDATE] User: {request.user}, Data: {request.data}")
            raise
