import logging
from datetime import datetime, timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from core.api.serializers.ai_serializer import ChatRequestSerializer, ChatResponseSerializer
from core.models import Transaction, Account
from utils.ai_service import get_ai_service

logger = logging.getLogger(__name__)


@extend_schema(
    summary="AI Financial Chat",
    description="Ask questions about your finances in natural language. The AI will analyze your transactions and accounts to provide helpful answers.",
    request=ChatRequestSerializer,
    responses={200: ChatResponseSerializer},
    examples=[
        OpenApiExample(
            'Simple Question',
            value={'question': 'How much did I spend last week?'},
            request_only=True
        ),
        OpenApiExample(
            'Account Balance',
            value={'question': 'What is my total balance?'},
            request_only=True
        ),
        OpenApiExample(
            'Transaction Search',
            value={'question': 'Show me my biggest expense this month'},
            request_only=True
        )
    ],
    tags=['AI Assistant']
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_chat(request):
    """
    AI-powered financial chat assistant
    
    Processes natural language questions about user's finances and returns
    intelligent responses based on transaction history and account data.
    """
    logger.info(f"[AI_CHAT] Request from user: {request.user}")
    
    # Validate request
    serializer = ChatRequestSerializer(data=request.data)
    if not serializer.is_valid():
        logger.warning(f"[AI_CHAT] Invalid request: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    question = serializer.validated_data['question']
    logger.info(f"[AI_CHAT] Question: {question}")
    
    try:
        # Gather user's financial context
        context = _build_user_context(request.user)
        
        # Get AI service and process question
        ai_service = get_ai_service()
        answer = ai_service.chat(question, context)
        
        # Prepare response
        response_data = {
            'question': question,
            'answer': answer,
            'timestamp': datetime.now()
        }
        
        logger.info(f"[AI_CHAT] Successfully processed question for user: {request.user}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"[AI_CHAT] Error processing question: {str(e)}", exc_info=True)
        return Response(
            {
                'error': 'Failed to process your question',
                'detail': 'Please try again or rephrase your question'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


def _build_user_context(user) -> dict:
    """
    Build comprehensive financial context for the user
    
    Args:
        user: The authenticated user
    
    Returns:
        Dictionary containing user's financial data
    """
    # Get user's accounts
    accounts = Account.objects.filter(user=user).values(
        'id', 'name', 'type', 'balance'
    )
    
    # Get recent transactions (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    transactions = Transaction.objects.filter(
        user=user,
        date__gte=thirty_days_ago
    ).order_by('-date').values(
        'id', 'type', 'amount', 'reason', 'date', 'account__name'
    )
    
    # Calculate total balance
    total_balance = sum(float(acc['balance']) for acc in accounts)
    
    # Build context dictionary
    context = {
        'user_name': user.first_name or 'User',
        'accounts': list(accounts),
        'transactions': list(transactions),
        'total_balance': total_balance
    }
    
    logger.debug(f"[AI_CHAT] Built context: {len(accounts)} accounts, {len(transactions)} transactions")
    
    return context
