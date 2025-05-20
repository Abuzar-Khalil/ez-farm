from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from user.serializers import UserSerializer, EmployeeSerializer
from django.http import HttpResponse

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """Only allow owners of an object or admins to edit it."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj == request.user or request.user.is_staff


class CanManageEmployees(permissions.BasePermission):
    """Only allow users with employee management permission."""

    def has_permission(self, request, view):
        return getattr(request.user, "can_manage_employees", False)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing user information."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_farm_owner', 'role']
    search_fields = ['email', 'first_name', 'last_name', 'farm_name']
    ordering_fields = ['email', 'date_joined', 'last_name']

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.action == 'employees':
            return EmployeeSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        """
        Return the currently authenticated user's full profile,
        including permissions.
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'])
    def employees(self, request):
        """
        List all employees for the current user or create a new employee.
        """
        if not getattr(request.user, "can_manage_employees", False):
            return Response(
                {"detail": "You do not have permission to manage employees."},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'GET':
            employees = User.objects.filter(employer=request.user)
            serializer = EmployeeSerializer(employees, many=True, context={'request': request})
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = EmployeeSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save(employer=request.user, is_farm_owner=False)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'put', 'patch', 'delete'])
    def employee(self, request, pk=None):
        """
        Retrieve, update or delete an employee by ID.
        """
        if not getattr(request.user, "can_manage_employees", False):
            return Response(
                {"detail": "You do not have permission to manage employees."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            employee = User.objects.get(pk=pk, employer=request.user)
        except User.DoesNotExist:
            return Response(
                {"detail": "Employee not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if request.method == 'GET':
            serializer = EmployeeSerializer(employee, context={'request': request})
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = EmployeeSerializer(employee, data=request.data, partial=partial, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'DELETE':
            employee.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

def user_view(request):
    return HttpResponse("User view is working!")
