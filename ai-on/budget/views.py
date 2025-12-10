from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema
from .models import Budget
from .serializers import BudgetSerializer, BudgetListSerializer
from .services import process_budget_generation, process_budget_operation

class BudgetGenerateView(APIView):
    """
    Endpoint to generate budgets using AI based on user profile and history.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        responses={200: BudgetSerializer(many=True)},
        description="Generate budgets using AI based on user profile and history."
    )
    def post(self, request):
        result = process_budget_generation(request.user)
        if result['type'] == 'success':
            return Response(result['data'], status=status.HTTP_200_OK)
        else:
            return Response(result['data'], status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BudgetViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return BudgetListSerializer
        return BudgetSerializer

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Manual creation not allowed. Use generate.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def perform_update(self, serializer):
        validated_data = serializer.validated_data
        instance = serializer.instance
        
        # Build natural language message describing the change
        changes = []
        if 'budget' in validated_data:
            changes.append(f"change budget to {validated_data['budget']}")
        if 'spent' in validated_data:
            changes.append(f"update spent to {validated_data['spent']}")
        
        # Save the update first
        updated_instance = serializer.save()
        
        # Construct message and call AI
        if changes:
            message = f"I want to edit '{instance.title}': {', '.join(changes)}"
            
            # Check for overspending
            if updated_instance.spent > updated_instance.budget:
                message += f". Note: This is overspending (spent {updated_instance.spent} exceeds budget {updated_instance.budget})."
            
            process_budget_operation(self.request.user, message)

    def perform_destroy(self, instance):
        user = self.request.user
        title = instance.title
        
        # Delete the instance first
        instance.delete()
        
        # Call AI with natural language message
        message = f"I want to delete '{title}'"
        process_budget_operation(user, message)
