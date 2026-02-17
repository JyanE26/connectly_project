from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import (
    require_group, require_any_group, IsPostAuthor, IsCommentAuthor, 
    IsAdminOrReadOnly, IsAuthorOrReadOnly, IsModeratorOrAdmin
)
from singletons.config_manager import ConfigManager
from singletons.logger_singleton import LoggerSingleton


class UserListCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Create token for new user
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'user': serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        logger = LoggerSingleton().get_logger()
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            # Get or create token for user
            token, created = Token.objects.get_or_create(user=user)
            # Get user groups/roles
            groups = user.groups.values_list('name', flat=True)
            
            # Log successful authentication
            logger.log_security_event(
                event_type="USER_LOGIN_SUCCESS",
                details=f"User {username} authenticated successfully",
                user=user
            )
            
            return Response({
                'message': 'Authentication successful!',
                'user_id': user.id,
                'username': user.username,
                'groups': list(groups),
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
            # Log failed authentication attempt
            logger.log_security_event(
                event_type="USER_LOGIN_FAILED",
                details=f"Failed login attempt for username: {username}",
                user=None
            )
            
            return Response({
                'error': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "message": "Authenticated!",
            "user": request.user.username,
            "user_id": request.user.id
        })


class LogoutView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Error logging out"}, status=status.HTTP_400_BAD_REQUEST)


class PostListCreate(APIView):
    def get(self, request):
        logger = LoggerSingleton().get_logger()
        config = ConfigManager()
        page_size = config.get_setting("DEFAULT_PAGE_SIZE")
        
        # Apply pagination using config
        posts = Post.objects.all()[:page_size]
        serializer = PostSerializer(posts, many=True)
        
        # Include pagination info in response
        response_data = {
            'posts': serializer.data,
            'pagination': {
                'page_size': page_size,
                'total_count': Post.objects.count()
            }
        }
        
        # Log analytics if enabled
        if config.get_setting("ENABLE_ANALYTICS"):
            logger.log_performance_metric(
                metric_name="POSTS_RETRIEVED",
                value=len(posts),
                details=f"Page size: {page_size}"
            )
        
        # Log API request
        logger.log_api_request(
            method="GET",
            endpoint="/posts/posts/",
            user=request.user if request.user.is_authenticated else None,
            status_code=200
        )
        
        return Response(response_data)


    def post(self, request):
        logger = LoggerSingleton().get_logger()
        config = ConfigManager()
        
        # Check if user has permission to create posts
        if not request.user.is_authenticated:
            logger.log_security_event(
                event_type="UNAUTHORIZED_ACCESS_ATTEMPT",
                details="Attempted to create post without authentication",
                user=None
            )
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Apply rate limiting from config
        rate_limit = config.get_setting("RATE_LIMIT")
        
        # For demo purposes, we'll just log the rate limit check
        if config.get_setting("ENABLE_ANALYTICS"):
            logger.log_performance_metric(
                metric_name="RATE_LIMIT_CHECK",
                value=rate_limit,
                details="Rate limit applied to post creation"
            )
        
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            post = serializer.save()
            
            # Log successful post creation
            logger.log_api_request(
                method="POST",
                endpoint="/posts/posts/",
                user=request.user,
                status_code=201
            )
            
            logger.log_performance_metric(
                metric_name="POST_CREATED",
                value=1,
                details=f"Post ID: {post.id}"
            )
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Log validation errors
            logger.log_api_request(
                method="POST",
                endpoint="/posts/posts/",
                user=request.user if request.user.is_authenticated else None,
                status_code=400
            )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            serializer = PostSerializer(post, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
            self.check_object_permissions(request, post)
            post.delete()
            return Response({'message': 'Post deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)


class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCommentAuthor]

    def get(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            self.check_object_permissions(request, comment)
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            self.check_object_permissions(request, comment)
            serializer = CommentSerializer(comment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            self.check_object_permissions(request, comment)
            comment.delete()
            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)


# Admin-only views
class AdminUserManagement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsModeratorOrAdmin]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
