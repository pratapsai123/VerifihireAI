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
            scoped_ids = get_scoped_user_ids(user_profile)
            if scoped_ids is None:
                # App Admin
                roles = JobRole.objects.filter(company=user_profile.company, is_deleted=False)
            else:
                # Scoped: only roles created by users in this user's reporting hierarchy
                roles = JobRole.objects.filter(
                    company=user_profile.company,
                    created_by_id__in=scoped_ids,
                    is_deleted=False
                )
        else:
            roles = JobRole.objects.filter(is_deleted=False)
            
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

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def job_role_delete_view(request, pk):
    """
    DELETE: Remove a JobRole.
    """
    try:
        role = JobRole.objects.get(pk=pk)
    except JobRole.DoesNotExist:
        return Response({'error': 'JobRole not found'}, status=status.HTTP_404_NOT_FOUND)
        
    user_profile = getattr(request.user, 'profile', None)
    if not user_profile or not user_profile.company:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    # Basic permission check: users from the same company can delete
    if role.company and user_profile.company != role.company:
        return Response({'error': 'Not authorized to delete this role'}, status=status.HTTP_403_FORBIDDEN)
        
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

