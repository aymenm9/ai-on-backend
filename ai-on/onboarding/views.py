from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse
from users.models import UserProfile
from .serializers import OnboardingQuestionResponseSerializer, OnboardingAnswerSerializer


class OnboardingView(APIView):
    """
    Onboarding conversation endpoint.
    
    GET: Get current question
    POST: Submit answer and get next question
    
    Note: Check onboarding status via /api/users/me/ endpoint
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get current onboarding question",
        description="""
        Returns the current onboarding question.
        
        **Important**: Before calling this endpoint, check the user's onboarding_status 
        via `/api/users/me/`. If status is 'completed', don't call this endpoint.
        
        Question types:
        - 'direct': Free text input (no options)
        - 'radio': Single choice (with options array)
        - 'checkboxes': Multiple choice (with options array)
        """,
        responses={
            200: OpenApiResponse(
                response=OnboardingQuestionResponseSerializer,
                description="Current onboarding question"
            ),
            400: OpenApiResponse(description="Onboarding already completed"),
        },
        tags=["Onboarding"]
    )
    def get(self, request):
        """Get current onboarding question."""
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        # Check if onboarding is already completed
        if profile.onboarding_status == 'completed':
            return Response({
                "detail": "Onboarding already completed. Check /api/users/me/ for status."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Start onboarding if not started
        if profile.onboarding_status == 'not_started':
            profile.onboarding_status = 'in_progress'
            profile.save()
        
        # Call AI agent to get first/next question
        from .services import process_onboarding_turn
        
        result = process_onboarding_turn(user=user, user_message=None)
        
        if result["type"] == "question":
            return Response(result["data"], status=status.HTTP_200_OK)
        elif result["type"] == "finsh":
            # This shouldn't happen on GET, but handle it
            return Response({
                "detail": "Onboarding completed unexpectedly."
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(result["data"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        summary="Submit answer to onboarding question",
        description="""
        Submit user's answer to the current onboarding question.
        Returns the next question.
        
        **When onboarding is complete**: The response will have an empty body and 
        the user's onboarding_status will be set to 'completed'. Check `/api/users/me/` 
        to confirm completion.
        
        Answer format depends on question type:
        - 'direct': {"answer": "text or number"}
        - 'radio': {"answer": "selected_option"}
        - 'checkboxes': {"answer": ["option1", "option2"]}
        """,
        request=OnboardingAnswerSerializer,
        responses={
            200: OpenApiResponse(
                response=OnboardingQuestionResponseSerializer,
                description="Next question"
            ),
            200: OpenApiResponse(
                description="Onboarding completed successfully. Returns {'type': 'finsh'}"
            ),
            400: OpenApiResponse(description="Invalid answer or onboarding not in progress"),
        },
        tags=["Onboarding"]
    )
    def post(self, request):
        """Submit answer and get next question."""
        user = request.user
        
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return Response({
                "detail": "Profile not found. Call GET first to start onboarding."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate onboarding status
        if profile.onboarding_status == 'completed':
            return Response({
                "detail": "Onboarding already completed."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if profile.onboarding_status == 'not_started':
            return Response({
                "detail": "Onboarding not started. Call GET first."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate answer
        serializer = OnboardingAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        answer = serializer.validated_data['answer']
        
        # Convert answer to string for the AI agent
        if isinstance(answer, list):
            user_message = ", ".join(answer)
        else:
            user_message = str(answer)
        
        # Call AI agent with user's answer
        from .services import process_onboarding_turn
        
        result = process_onboarding_turn(user=user, user_message=user_message)
        
        if result["type"] == "question":
            # Return next question
            return Response(result["data"], status=status.HTTP_200_OK)
        elif result["type"] == "finsh":
            # Onboarding finished!
            return Response({"type": "finsh"}, status=status.HTTP_200_OK)
        else:
            # Error occurred
            return Response(result["data"], status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OnboardingResetView(APIView):
    """Reset onboarding status (for testing/debugging)."""
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Reset onboarding status",
        description="Resets the user's onboarding status to 'not_started'. Useful for testing.",
        responses={
            200: OpenApiResponse(description="Onboarding reset successfully"),
        },
        tags=["Onboarding"]
    )
    def post(self, request):
        """Reset onboarding to not_started."""
        user = request.user
        profile = UserProfile.objects.get(user=user)
        profile.onboarding_status = 'not_started'
        profile.save()
        
        return Response({
            "detail": "Onboarding status reset to 'not_started'."
        }, status=status.HTTP_200_OK)

