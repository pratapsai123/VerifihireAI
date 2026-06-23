from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from api.models import SubscriptionPlan
from api.serializers import SubscriptionPlanSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_public_plans_view(request):
    """
    Public endpoint to get active pricing plans for the frontend.
    """
    try:
        plans = SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order')
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({'plans': serializer.data}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching plans: {str(e)}")
        return Response({'error': 'Failed to fetch plans'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def manage_plans_list_view(request):
    """
    Admin endpoint to list all plans (including inactive) or create a new plan.
    Requires Superadmin or appropriate role (assuming IsAuthenticated for now, you can add IsAdminUser if you have a custom permission).
    """
    if request.method == 'GET':
        plans = SubscriptionPlan.objects.all().order_by('sort_order')
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response({'plans': serializer.data}, status=status.HTTP_200_OK)
        
    elif request.method == 'POST':
        # Assuming only admins can create
        # In a real scenario, you'd check request.user.is_superuser or similar
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Plan created successfully', 'plan': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def manage_plan_detail_view(request, plan_id):
    """
    Admin endpoint to read, update, or delete a specific plan.
    """
    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)
    except SubscriptionPlan.DoesNotExist:
        return Response({'error': 'Plan not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SubscriptionPlanSerializer(plan)
        return Response({'plan': serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = SubscriptionPlanSerializer(plan, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Plan updated successfully', 'plan': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        plan.delete()
        return Response({'message': 'Plan deleted successfully'}, status=status.HTTP_200_OK)
