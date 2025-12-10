from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import ChatMessageSerializer, ChatResponseSerializer, ChatHistoryItemSerializer
from .services import process_chatbot_message, get_or_create_chatbot_agent
from agents.services import get_agent_history, clear_agent_history


class ChatView(APIView):
    """
    Endpoint to send messages to the chatbot and receive responses.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=ChatMessageSerializer,
        responses={
            200: ChatResponseSerializer,
            500: OpenApiResponse(description="Internal server error")
        },
        description="Send a message to the chatbot and receive a response. The chatbot can handle general conversation, profile updates, and delegate complex tasks to specialized agents."
    )
    def post(self, request):
        serializer = ChatMessageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_message = serializer.validated_data['msg']
        
        result = process_chatbot_message(request.user, user_message)
        
        if result['type'] == 'success':
            return Response(
                {"msg": result['data']['message']},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"msg": result['data'].get('message', 'An error occurred')},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryView(APIView):
    """
    Endpoint to retrieve chat history (excluding function calls).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: ChatHistoryItemSerializer(many=True),
        },
        description="Retrieve the chat history for the current user. Returns only user and model messages, excluding function calls."
    )
    def get(self, request):
        agent = get_or_create_chatbot_agent()
        history = get_agent_history(agent, request.user)
        
        # Filter out function calls and format for response
        filtered_history = []
        for content in history:
            role = content.role
            for part in content.parts:
                # Only include text messages, skip function calls and responses
                if hasattr(part, 'text') and part.text:
                    filtered_history.append({
                        "role": role,
                        "msg": part.text
                    })
        
        return Response(filtered_history, status=status.HTTP_200_OK)


class ChatResetView(APIView):
    """
    Endpoint to reset/clear chat history.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={
            200: OpenApiResponse(description="Chat history cleared successfully"),
        },
        description="Clear the chat history for the current user."
    )
    def post(self, request):
        agent = get_or_create_chatbot_agent()
        clear_agent_history(agent, request.user)
        
        return Response(
            {"message": "Chat history cleared successfully"},
            status=status.HTTP_200_OK
        )
