from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserRegistrationSerializer, UserListSerializer, UserApproveSerializer

# ---------------------------
# Public Endpoints
# ---------------------------

class RegisterView(generics.CreateAPIView):
    """
    Allows anyone to register a new user.
    New users are created with is_approved=False (pending admin approval).
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(APIView):
    """
    Custom login that only allows approved users (is_approved=True).
    Returns JWT tokens on success.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user and user.is_approved:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        elif user and not user.is_approved:
            return Response(
                {'error': 'Account not approved yet. Please wait for admin approval.'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(APIView):
    """
    Returns the profile of the currently authenticated user.
    Includes is_staff so frontend can determine admin status.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_approved': user.is_approved,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
        })


# ---------------------------
# Admin‑Only Endpoints
# ---------------------------

class AdminUserListView(generics.ListAPIView):
    """
    Lists all users. Only accessible to admin users (is_staff=True).
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminUserApproveView(generics.UpdateAPIView):
    """
    Approves a user (sets is_approved=True). Admin only.
    """
    queryset = User.objects.all()
    serializer_class = UserApproveSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_approved = True
        instance.save()
        return Response(UserListSerializer(instance).data)


class AdminUserMakeStaffView(APIView):
    """
    Promotes a user to staff (admin). Admin only.
    """
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            user.is_staff = True
            user.save()
            return Response({'message': f'{user.username} is now a staff member.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserDeleteView(generics.DestroyAPIView):
    """
    Deletes a user. Admin only.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


# ---------------------------
# Initial Admin Creation (One‑Time)
# ---------------------------

class AdminExistsView(APIView):
    """
    Checks whether any staff (admin) user exists.
    Used by frontend to decide whether to show the initial admin creation form.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        exists = User.objects.filter(is_staff=True).exists()
        return Response({'admin_exists': exists})


class CreateInitialAdminView(APIView):
    """
    Creates the very first admin user. This endpoint only works if no staff user exists yet.
    Once an admin exists, further calls will be rejected.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if User.objects.filter(is_staff=True).exists():
            return Response(
                {'error': 'Admin already exists. Cannot create another initial admin.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  
            user.is_staff = True
            user.is_superuser = True  
            user.is_approved = True
            user.save()
            return Response(
                {'message': 'Initial admin created successfully. You can now log in.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)