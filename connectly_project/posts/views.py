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
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user is not None:
            # Get or create token for user
            token, created = Token.objects.get_or_create(user=user)
            # Get user groups/roles
            groups = user.groups.values_list('name', flat=True)
            return Response({
                'message': 'Authentication successful!',
                'user_id': user.id,
                'username': user.username,
                'groups': list(groups),
                'token': token.key
            }, status=status.HTTP_200_OK)
        else:
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
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


    def post(self, request):
        # Check if user has permission to create posts
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
