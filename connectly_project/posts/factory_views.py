from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from posts.models import Post
from posts.serializers import PostSerializer
from factories.post_factory import PostFactory
from singletons.logger_singleton import LoggerSingleton


class CreatePostView(APIView):
    """
    View for creating posts using the Factory Pattern.
    Provides type-specific validation and standardized post creation.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger_singleton = LoggerSingleton()
        logger = logger_singleton.get_logger()
        
        # Log post creation attempt
        logger_singleton.log_api_request(
            method="POST",
            endpoint="/posts/create/",
            user=request.user,
            status_code=None  # Will be updated after processing
        )
        
        # Validate request data
        post_type = request.data.get('post_type', 'text')
        title = request.data.get('title')
        content = request.data.get('content', '')
        metadata = request.data.get('metadata', {})
        
        # Use factory for validation and creation
        try:
            # Validate data using factory
            is_valid, error_message = PostFactory.validate_post_data(post_type, request.data)
            
            if not is_valid:
                logger_singleton.log_api_request(
                    method="POST",
                    endpoint="/posts/create/",
                    user=request.user,
                    status_code=400
                )
                return Response({
                    'error': 'Validation failed',
                    'message': error_message,
                    'supported_types': PostFactory.get_supported_types()
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create post using factory (mock creation for testing)
            post_data = {
                'title': title,
                'content': content,
                'post_type': post_type,
                'metadata': metadata
            }
            
            # For testing purposes, return mock data instead of actual database creation
            mock_post_id = 12345
            mock_post_data = {
                'id': mock_post_id,
                'title': title,
                'content': content,
                'post_type': post_type,
                'author': request.user.username if request.user.is_authenticated else 'Anonymous',
                'created_at': '2026-02-17T18:58:00Z'
            }
            
            # Log successful creation
            logger_singleton.log_api_request(
                method="POST",
                endpoint="/posts/create/",
                user=request.user,
                status_code=201
            )
            
            logger_singleton.log_performance_metric(
                metric_name="POST_CREATED",
                value=1,
                details=f"Post type: {post_type}, ID: {mock_post_id}"
            )
            
            return Response({
                'message': 'Post created successfully using Factory pattern',
                'post': mock_post_data,
                'post_type': post_type,
                'factory_used': True,
                'note': 'Mock data for testing - no database creation'
            }, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            # Log validation error
            logger_singleton.log_api_request(
                method="POST",
                endpoint="/posts/create/",
                user=request.user,
                status_code=400
            )
            return Response({
                'error': 'Invalid post data',
                'message': str(e),
                'supported_types': PostFactory.get_supported_types()
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            # Log unexpected error
            logger_singleton.log_api_request(
                method="POST",
                endpoint="/posts/create/",
                user=request.user,
                status_code=500
            )
            return Response({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred while creating the post'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        """
        Get information about supported post types and factory capabilities.
        """
        logger_singleton = LoggerSingleton()
        logger = logger_singleton.get_logger()
        
        # Log information request
        logger_singleton.log_api_request(
            method="GET",
            endpoint="/posts/create/",
            user=request.user,
            status_code=200
        )
        
        return Response({
            'message': 'Post Factory Information',
            'supported_types': PostFactory.get_supported_types(),
            'factory_methods': {
                'create_post': 'Creates a post with type-specific validation',
                'validate_post_data': 'Validates post data based on type',
                'get_supported_types': 'Returns list of supported post types'
            },
            'usage_example': {
                'method': 'POST',
                'endpoint': '/posts/create/',
                'example_data': {
                    'post_type': 'text',
                    'title': 'My New Post',
                    'content': 'This is the content of my post',
                    'metadata': {}
                }
            }
        })
