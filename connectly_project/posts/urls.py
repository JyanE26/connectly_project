from django.urls import path
from .views import (
    UserListCreate, PostListCreate, CommentListCreate, LoginView, AdminUserManagement,
    PostDetailView, CommentDetailView, ProtectedView, LogoutView
)
from .config_views import ConfigView
from .factory_views import CreatePostView


urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('protected/', ProtectedView.as_view(), name='protected'),
    path('config/', ConfigView.as_view(), name='config-management'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/create/', CreatePostView.as_view(), name='post-create-factory'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('admin/users/', AdminUserManagement.as_view(), name='admin-user-management'),
]