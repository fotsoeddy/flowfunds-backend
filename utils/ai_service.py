"""
FlowFunds AI Service
Handles all AI-related operations using DeepSeek API
"""
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Any
from django.conf import settings
from openai import OpenAI

logger = logging.getLogger(__name__)


class FlowFundsAI:
    """
    AI Service for FlowFunds financial assistant
    Uses DeepSeek API for natural language understanding and responses
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        self.model = "deepseek-chat"
    
    def chat(self, user_question: str, user_context: Dict[str, Any]) -> str:
        """
        Process user question with financial context and return AI response
        
        Args:
            user_question: The user's natural language question
            user_context: Dictionary containing user's financial data
        
        Returns:
            AI-generated response string
        """
        try:
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(user_question, user_context)
            
            logger.info(f"[AI_CHAT] Processing question: {user_question[:50]}...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent financial advice
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            logger.info(f"[AI_CHAT] Generated response: {answer[:50]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"[AI_CHAT] Error: {str(e)}", exc_info=True)
            return "I'm sorry, I encountered an error processing your question. Please try again."
    
    def _build_system_prompt(self) -> str:
        """Build the system prompt that defines AI behavior"""
        return """You are FlowFunds AI Assistant, a friendly financial advisor for the FlowFunds personal finance app.

ABOUT FLOWFUNDS:
FlowFunds is a money management app that helps users track their finances across multiple accounts (Mobile Money, Orange Money, Cash, Bank). Users can record income, expenses, and savings, then view analytics and insights.

HOW TO USE FLOWFUNDS (explain this when asked):
1. **Add Accounts**: Go to Accounts page → Add new account (MoMo, Orange Money, Cash, or Bank)
2. **Record Income**: Click "Add Transaction" → Select "Income" → Enter amount and reason → Choose which account received the money
3. **Record Expenses**: Click "Add Transaction" → Select "Expense" → Enter amount and reason → Choose which account paid
4. **Track Savings**: Use "Save" transaction type to move money to savings
5. **View Analytics**: Check the Accounts page for daily income vs expense graphs
6. **Check Balance**: Home page shows total balance across all accounts

KEY FEATURES:
- Multiple account types (MoMo, OM, Cash, Bank)
- Transaction tracking (Income, Expense, Save)
- Daily analytics graphs
- Balance privacy toggle
- AI assistant (that's you!)

Your role:
- Answer questions about the user's transactions, accounts, and spending
- Explain how to use FlowFunds features when asked
- Be conversational, warm, and encouraging
- Keep responses SHORT (2-4 sentences max)
- Use simple language, avoid jargon
- Format currency as "50,000 XAF" (with commas, no decimals)
- Use dates like "January 15" or "last week"

Response style:
- NO markdown formatting (no **, ###, bullets)
- Write naturally, like texting a friend
- Be positive and encouraging
- Give ONE actionable tip when relevant
- Never make up data - only use what's provided

Example responses:
Q: "What is this app about?"
A: "FlowFunds helps you track your money across all your accounts - MoMo, Orange Money, Cash, and Bank. You can record income and expenses, then see graphs showing where your money goes. Want me to show you how to get started?"

Q: "How do I add money?"
A: "To record income, tap 'Add Transaction', choose 'Income', enter the amount and reason (like 'Salary' or 'Gift'), then select which account received it. That's it!"

Q: "How do I track expenses?"
A: "Same as income but choose 'Expense' instead. Enter the amount, what you spent on (like 'Transport' or 'Food'), and which account you paid from. FlowFunds will track it all for you."

Remember: Short, friendly, conversational. Help users understand both their finances AND how to use the app."""
    
    def _build_user_prompt(self, question: str, context: Dict[str, Any]) -> str:
        """Build the user prompt with question and financial context"""
        
        # Extract context data
        accounts = context.get('accounts', [])
        transactions = context.get('transactions', [])
        total_balance = context.get('total_balance', 0)
        user_name = context.get('user_name', 'User')
        
        # Format accounts summary
        accounts_summary = self._format_accounts(accounts)
        
        # Format recent transactions
        transactions_summary = self._format_transactions(transactions)
        
        # Calculate key metrics
        metrics = self._calculate_metrics(transactions)
        
        prompt = f"""User: {user_name}

FINANCIAL OVERVIEW:
Total Balance: {total_balance:,.0f} XAF

ACCOUNTS:
{accounts_summary}

RECENT TRANSACTIONS (Last 30 days):
{transactions_summary}

KEY METRICS:
- Total Income (30 days): {metrics['total_income']:,.0f} XAF
- Total Expenses (30 days): {metrics['total_expenses']:,.0f} XAF
- Net Change: {metrics['net_change']:,.0f} XAF
- Transaction Count: {metrics['transaction_count']}

USER QUESTION:
{question}

Please answer the question based on the financial data provided above. Be specific and use actual numbers from the data."""
        
        return prompt
    
    def _format_accounts(self, accounts: List[Dict]) -> str:
        """Format accounts list for prompt"""
        if not accounts:
            return "No accounts found"
        
        lines = []
        for acc in accounts:
            acc_type = acc.get('type', 'unknown').upper()
            name = acc.get('name', 'Account')
            balance = acc.get('balance', 0)
            lines.append(f"- {name} ({acc_type}): {float(balance):,.0f} XAF")
        
        return "\n".join(lines)
    
    def _format_transactions(self, transactions: List[Dict]) -> str:
        """Format transactions list for prompt (last 20 transactions)"""
        if not transactions:
            return "No recent transactions"
        
        lines = []
        for txn in transactions[:20]:  # Limit to 20 most recent
            txn_type = txn.get('type', 'unknown')
            amount = txn.get('amount', 0)
            reason = txn.get('reason', 'No description')
            date = txn.get('date', '')
            
            # Format date
            try:
                dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                date_str = dt.strftime('%b %d')
            except:
                date_str = 'Unknown date'
            
            # Format type indicator
            type_indicator = {
                'income': '+',
                'expense': '-',
                'save': '→'
            }.get(txn_type, '?')
            
            lines.append(f"{date_str}: {type_indicator}{float(amount):,.0f} XAF - {reason}")
        
        return "\n".join(lines)
    
    def _calculate_metrics(self, transactions: List[Dict]) -> Dict[str, float]:
        """Calculate key financial metrics from transactions"""
        total_income = 0
        total_expenses = 0
        
        for txn in transactions:
            amount = float(txn.get('amount', 0))
            txn_type = txn.get('type', '')
            
            if txn_type == 'income':
                total_income += amount
            elif txn_type == 'expense':
                total_expenses += amount
        
        return {
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_change': total_income - total_expenses,
            'transaction_count': len(transactions)
        }


# Singleton instance
_ai_service = None

def get_ai_service() -> FlowFundsAI:
    """Get or create AI service singleton"""
    global _ai_service
    if _ai_service is None:
        _ai_service = FlowFundsAI()
    return _ai_service
