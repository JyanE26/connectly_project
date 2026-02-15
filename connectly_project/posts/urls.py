from django.urls import path
from .views import (
    UserListCreate, PostListCreate, CommentListCreate, LoginView, AdminUserManagement,
    PostDetailView, CommentDetailView, ProtectedView, LogoutView
)


urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('admin/users/', AdminUserManagement.as_view(), name='admin-user-management'),
]