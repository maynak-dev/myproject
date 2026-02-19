from django.urls import path 
from .views import RegisterView, LoginView, UserProfileView,AdminUserListView, AdminUserApproveView, AdminUserMakeStaffView, AdminUserDeleteView, AdminExistsView, CreateInitialAdminView

urlpatterns = [
    # Public
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # Admin management
    path('admin/users/', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/approve/', AdminUserApproveView.as_view(), name='admin-approve'),
    path('admin/users/<int:pk>/make-staff/', AdminUserMakeStaffView.as_view(), name='admin-make-staff'),
    path('admin/users/<int:pk>/delete/', AdminUserDeleteView.as_view(), name='admin-delete'),

    # Initial admin setup
    path('admin/exists/', AdminExistsView.as_view(), name='admin-exists'),
    path('create-initial-admin/', CreateInitialAdminView.as_view(), name='create-initial-admin'),
]