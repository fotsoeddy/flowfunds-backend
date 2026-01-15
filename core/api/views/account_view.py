import logging
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.models import Account
from core.api.serializers.account_serializer import AccountSerializer, CreateAccountSerializer

logger = logging.getLogger(__name__)

@extend_schema(
    summary="List or Create Accounts",
    description="Get list of active accounts or create a new one.",
    examples=[
        OpenApiExample(
            'Create Account Example',
            value={
                'name': 'Orange Money Secondary',
                'number': '699123456',
                'type': 'om',
                'initial_balance': 10000
            },
            request_only=True
        )
    ]
)
class AccountListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        logger.debug(f"[ACCOUNT_LIST] Fetching accounts for user: {self.request.user}")
        try:
            queryset = Account.objects.filter(user=self.request.user, status=1)
            logger.info(f"[ACCOUNT_LIST] Found {queryset.count()} active accounts for user: {self.request.user}")
            return queryset
        except Exception as e:
            logger.error(f"[ACCOUNT_LIST] Error fetching accounts: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_LIST] User: {self.request.user}")
            raise

    def get_serializer_class(self):
        if self.request.method == 'POST':
            logger.debug(f"[ACCOUNT] Using CreateAccountSerializer for POST request")
            return CreateAccountSerializer
        logger.debug(f"[ACCOUNT] Using AccountSerializer for GET request")
        return AccountSerializer
    
    def list(self, request, *args, **kwargs):
        logger.info(f"[ACCOUNT_LIST] Account list request from user: {request.user}")
        
        try:
            queryset = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(queryset, many=True)
            logger.debug(f"[ACCOUNT_LIST] Returning {len(serializer.data)} accounts")
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"[ACCOUNT_LIST] Failed to list accounts: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_LIST] User: {request.user}")
            raise
    
    def create(self, request, *args, **kwargs):
        logger.info(f"[ACCOUNT_CREATE] Account creation attempt by user: {request.user}")
        logger.debug(f"[ACCOUNT_CREATE] Request data: {request.data}")
        
        try:
            serializer = self.get_serializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"[ACCOUNT_CREATE] Validation failed: {serializer.errors}")
                logger.debug(f"[ACCOUNT_CREATE] Invalid data: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"[ACCOUNT_CREATE] Validation successful, creating account")
            self.perform_create(serializer)
            
            headers = self.get_success_headers(serializer.data)
            logger.info(f"[ACCOUNT_CREATE] Account created successfully: {serializer.data.get('name')}")
            logger.debug(f"[ACCOUNT_CREATE] Created account data: {serializer.data}")
            
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            
        except Exception as e:
            logger.error(f"[ACCOUNT_CREATE] Account creation failed: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_CREATE] User: {request.user}, Data: {request.data}")
            return Response(
                {"error": "Account creation failed", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@extend_schema(summary="Retrieve, Update or Delete Account")
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        logger.debug(f"[ACCOUNT_DETAIL] Fetching accounts for user: {self.request.user}")
        try:
            queryset = Account.objects.filter(user=self.request.user)
            logger.debug(f"[ACCOUNT_DETAIL] User has {queryset.count()} total accounts")
            return queryset
        except Exception as e:
            logger.error(f"[ACCOUNT_DETAIL] Error fetching account queryset: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_DETAIL] User: {self.request.user}")
            raise
    
    def retrieve(self, request, *args, **kwargs):
        logger.info(f"[ACCOUNT_RETRIEVE] Account retrieval request from user: {request.user}")
        logger.debug(f"[ACCOUNT_RETRIEVE] Account ID: {kwargs.get('pk')}")
        
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            logger.info(f"[ACCOUNT_RETRIEVE] Account retrieved: {instance.name}")
            logger.debug(f"[ACCOUNT_RETRIEVE] Account data: {serializer.data}")
            return Response(serializer.data)
            
        except Account.DoesNotExist:
            logger.warning(f"[ACCOUNT_RETRIEVE] Account not found: {kwargs.get('pk')}")
            logger.debug(f"[ACCOUNT_RETRIEVE] User: {request.user}")
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"[ACCOUNT_RETRIEVE] Failed to retrieve account: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_RETRIEVE] User: {request.user}, Account ID: {kwargs.get('pk')}")
            raise
    
    def update(self, request, *args, **kwargs):
        logger.info(f"[ACCOUNT_UPDATE] Account update attempt by user: {request.user}")
        logger.debug(f"[ACCOUNT_UPDATE] Account ID: {kwargs.get('pk')}, Data: {request.data}")
        
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            logger.debug(f"[ACCOUNT_UPDATE] Updating account: {instance.name}")
            
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if not serializer.is_valid():
                logger.warning(f"[ACCOUNT_UPDATE] Validation failed: {serializer.errors}")
                logger.debug(f"[ACCOUNT_UPDATE] Invalid data: {request.data}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            self.perform_update(serializer)
            logger.info(f"[ACCOUNT_UPDATE] Account updated successfully: {instance.name}")
            logger.debug(f"[ACCOUNT_UPDATE] Updated data: {serializer.data}")
            
            return Response(serializer.data)
            
        except Account.DoesNotExist:
            logger.warning(f"[ACCOUNT_UPDATE] Account not found: {kwargs.get('pk')}")
            logger.debug(f"[ACCOUNT_UPDATE] User: {request.user}")
            return Response(
                {"error": "Account not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"[ACCOUNT_UPDATE] Update failed: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_UPDATE] User: {request.user}, Account ID: {kwargs.get('pk')}, Data: {request.data}")
            raise

    def perform_destroy(self, instance):
        logger.info(f"[ACCOUNT_DELETE] Soft delete attempt for account: {instance.name}")
        logger.debug(f"[ACCOUNT_DELETE] Account ID: {instance.id}, User: {self.request.user}")
        
        try:
            instance.status = 0  # Soft delete
            instance.save()
            logger.info(f"[ACCOUNT_DELETE] Account soft deleted successfully: {instance.name}")
            logger.debug(f"[ACCOUNT_DELETE] Account ID: {instance.id}")
            
        except Exception as e:
            logger.error(f"[ACCOUNT_DELETE] Soft delete failed: {str(e)}", exc_info=True)
            logger.error(f"[ACCOUNT_DELETE] Account: {instance.name}, ID: {instance.id}")
            raise
