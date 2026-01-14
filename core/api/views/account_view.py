from rest_framework import generics, status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from core.models import Account
from core.api.serializers.account_serializer import AccountSerializer, CreateAccountSerializer

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
        return Account.objects.filter(user=self.request.user, status=1) # Active accounts only

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateAccountSerializer
        return AccountSerializer

@extend_schema(summary="Retrieve, Update or Delete Account")
class AccountDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        instance.status = 0 # Soft delete
        instance.save()
