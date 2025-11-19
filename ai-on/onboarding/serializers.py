from rest_framework import serializers


class OnboardingQuestionResponseSerializer(serializers.Serializer):
    """
    Serializer for AI-generated onboarding questions.
    
    Question types:
    - 'direct': Free text question (no options)
    - 'radio': Single choice question (with options)
    - 'checkboxes': Multiple choice question (with options)
    
    Note: To check if onboarding is complete, use /api/users/me/ 
    and check the 'onboarding_status' field in the profile.
    """
    question = serializers.CharField(
        help_text="The question text"
    )
    question_type = serializers.ChoiceField(
        choices=['direct', 'radio', 'checkboxes'],
        help_text="Type of question: 'direct' (free text), 'radio' (single choice), 'checkboxes' (multiple choice)"
    )
    options = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="List of options for 'radio' or 'checkboxes' questions (null for 'direct' questions)"
    )


class OnboardingAnswerSerializer(serializers.Serializer):
    """
    Serializer for user's answer to onboarding question.
    
    For 'direct' questions: answer is a string
    For 'radio' questions: answer is a single string (selected option)
    For 'checkboxes' questions: answer is a list of strings (selected options)
    """
    answer = serializers.JSONField(
        help_text="User's answer: string for direct/radio, list of strings for checkboxes"
    )
