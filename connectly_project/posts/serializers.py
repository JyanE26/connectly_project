from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password
        )
        return user

    def to_representation(self, instance):
        """Exclude sensitive fields from responses"""
        data = super().to_representation(instance)
        # Remove sensitive fields that shouldn't be exposed
        sensitive_fields = ['password', 'is_superuser', 'is_staff', 'is_active', 'last_login', 'date_joined']
        for field in sensitive_fields:
            data.pop(field, None)
        return data


class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'content', 'author', 'author_username', 'created_at', 'comments']
        extra_kwargs = {
            'author': {'write_only': True}  # Use author_username for display
        }


class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    post_content_preview = serializers.CharField(source='post.content', read_only=True, max_length=50)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'author_username', 'post', 'post_content_preview', 'created_at']
        extra_kwargs = {
            'author': {'write_only': True},  # Use author_username for display
            'post': {'write_only': True}     # Use post_content_preview for display
        }

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value


class SafeUserSerializer(serializers.ModelSerializer):
    """Read-only serializer for public user information"""
    class Meta:
        model = User
        fields = ['id', 'username']  # Only expose non-sensitive public info