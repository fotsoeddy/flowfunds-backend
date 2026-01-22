from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for AI chat requests"""
    question = serializers.CharField(
        max_length=500,
        required=True,
        help_text="User's question in natural language"
    )
    
    def validate_question(self, value):
        """Validate question is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Question cannot be empty")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for AI chat responses"""
    question = serializers.CharField()
    answer = serializers.CharField()
    timestamp = serializers.DateTimeField()
