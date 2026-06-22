from .._imports import *
from api.models import JobRole

class JobRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobRole
        fields = ['id', 'title', 'description', 'created_at']

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def job_role_list_create_view(request):
    """
    GET: List all JobRoles for the user's company (or all if not tied to a company).
    POST: Create a new JobRole.
    """
    user_profile = getattr(request.user, 'profile', None)
    
    if request.method == 'GET':
        if user_profile and user_profile.company:
            from api._imports import get_scoped_user_ids
            scoped_ids = get_scoped_user_ids(user_profile)
            
            if scoped_ids is None:
                # App Admin / Company Admin see all company roles
                roles = JobRole.objects.filter(company=user_profile.company, is_deleted=False).order_by('-created_at')
            else:
                # HR / HR Manager see only their own and their direct reports' created roles
                roles = JobRole.objects.filter(
                    company=user_profile.company,
                    created_by_id__in=scoped_ids,
                    is_deleted=False
                ).order_by('-created_at')
        else:
            roles = JobRole.objects.filter(is_deleted=False).order_by('-created_at')
            
        serializer = JobRoleSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    elif request.method == 'POST':
        data = request.data
        title = data.get('title')
        description = data.get('description')
        
        if not title or not description:
            return Response({'error': 'Title and description are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        role = JobRole.objects.create(
            title=title,
            description=description,
            created_by=user_profile,
            company=user_profile.company if user_profile else None
        )
        serializer = JobRoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

def ensure_role_exists(title, description, user=None):
    """
    Utility to ensure a job role exists in the database.
    Used for auto-persisting custom roles.
    """
    if not title or not description:
        return None
    
    user_profile = getattr(user, 'profile', None) if user else None
    company = user_profile.company if user_profile else None
    
    # Try to find existing role (case-insensitive title match within the same company)
    existing_role = JobRole.objects.filter(
        title__iexact=title.strip(),
        company=company
    ).first()
    
    if existing_role:
        return existing_role
        
    # Create new role if not found
    return JobRole.objects.create(
        title=title.strip(),
        description=description,
        created_by=user_profile,
        company=company
    )

@api_view(['PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def job_role_detail_view(request, pk):
    """
    PUT/PATCH: Edit a JobRole.
    DELETE: Remove a JobRole.
    """
    try:
        role = JobRole.objects.get(pk=pk)
    except JobRole.DoesNotExist:
        return Response({'error': 'JobRole not found'}, status=status.HTTP_404_NOT_FOUND)
        
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    # Basic permission check: users from the same company can modify/delete
    if role.company and user_profile.company != role.company:
        return Response({'error': 'Not authorized for this role'}, status=status.HTTP_403_FORBIDDEN)

    # Strict RBAC: If user is scoped, ensure they can only modify/delete roles in their hierarchy
    from api._imports import get_scoped_user_ids
    scoped_ids = get_scoped_user_ids(user_profile)
    if scoped_ids is not None and role.created_by_id not in scoped_ids:
        return Response({'error': 'Not authorized for this role'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ['PUT', 'PATCH']:
        title = request.data.get('title')
        description = request.data.get('description')
        
        if request.method == 'PUT' and (not title or not description):
            return Response({'error': 'Title and description are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        if title is not None:
            role.title = title.strip()
        if description is not None:
            role.description = description
            
        role.save()
        serializer = JobRoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # Use centralized helper to handle policy and workflow
        response, handled = handle_deletion_request(
            user_profile=user_profile,
            company=user_profile.company,
            content_type='JobRole',
            object_id=role.id,
            object_repr=f"Job Role: {role.title}",
            reason=request.data.get('reason')
        )
        
        if handled:
            return response

        role.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

