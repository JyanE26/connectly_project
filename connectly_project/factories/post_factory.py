from posts.models import Post


class PostFactory:
    """
    Factory class for creating different types of posts with consistent validation.
    Ensures standardized post creation across the API.
    """
    
    # Define post types as constants for consistency
    POST_TYPES = {
        'text': 'Standard text post',
        'image': 'Post with image attachment',
        'video': 'Post with video attachment',
        'article': 'Long-form article post',
        'poll': 'Interactive poll post'
    }
    
    @staticmethod
    def create_post(post_type, title=None, content='', author=None, metadata=None):
        """
        Create a post with type-specific validation and default values.
        
        Args:
            post_type (str): Type of post to create
            title (str, optional): Title of the post
            content (str): Content of the post
            author (User): Author of the post
            metadata (dict, optional): Additional metadata for the post
            
        Returns:
            Post: Created post object
            
        Raises:
            ValueError: If post_type is invalid or required metadata is missing
        """
        
        # Validate post type
        if post_type not in PostFactory.POST_TYPES:
            raise ValueError(f"Invalid post type. Must be one of: {list(PostFactory.POST_TYPES.keys())}")
        
        # Type-specific validation
        if post_type == 'image' and metadata:
            if 'file_size' not in metadata:
                raise ValueError("Image posts require 'file_size' in metadata")
            if 'file_type' not in metadata:
                raise ValueError("Image posts require 'file_type' in metadata")
        
        if post_type == 'video' and metadata:
            if 'duration' not in metadata:
                raise ValueError("Video posts require 'duration' in metadata")
            if 'file_size' not in metadata:
                raise ValueError("Video posts require 'file_size' in metadata")
        
        if post_type == 'article' and not title:
            raise ValueError("Article posts require a title")
        
        # Set default title based on post type
        if not title:
            title = PostFactory._get_default_title(post_type)
        
        # Create the post with validated data
        post = Post.objects.create(
            title=title,
            content=content,
            author=author,
            post_type=post_type,
            metadata=metadata or {}
        )
        
        return post
    
    @staticmethod
    def _get_default_title(post_type):
        """
        Generate default title based on post type.
        
        Args:
            post_type (str): Type of post
            
        Returns:
            str: Default title for the post type
        """
        default_titles = {
            'text': 'New Text Post',
            'image': 'New Image Post',
            'video': 'New Video Post',
            'article': 'New Article',
            'poll': 'New Poll'
        }
        
        return default_titles.get(post_type, 'Untitled Post')
    
    @staticmethod
    def get_supported_types():
        """
        Get list of all supported post types.
        
        Returns:
            list: Available post types with descriptions
        """
        return PostFactory.POST_TYPES
    
    @staticmethod
    def validate_post_data(post_type, data):
        """
        Validate post data based on type requirements.
        
        Args:
            post_type (str): Type of post being created
            data (dict): Post data to validate
            
        Returns:
            tuple: (is_valid, error_message)
        """
        try:
            # Basic validation for all post types
            if not data.get('content'):
                return False, "Content is required for all post types"
            
            # Type-specific validation
            if post_type == 'image':
                return PostFactory._validate_image_post(data)
            elif post_type == 'video':
                return PostFactory._validate_video_post(data)
            elif post_type == 'article':
                return PostFactory._validate_article_post(data)
            elif post_type == 'poll':
                return PostFactory._validate_poll_post(data)
            elif post_type == 'text':
                return True, None  # Text posts are always valid with content
            else:
                return False, f"Invalid post type. Must be one of: {list(PostFactory.POST_TYPES.keys())}"
                
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def _validate_image_post(data):
        """Validate image post specific requirements."""
        metadata = data.get('metadata', {})
        required_fields = ['file_size', 'file_type']
        
        for field in required_fields:
            if field not in metadata:
                return False, f"Image posts must include {field} in metadata"
        
        return True, None
    
    @staticmethod
    def _validate_video_post(data):
        """Validate video post specific requirements."""
        metadata = data.get('metadata', {})
        required_fields = ['duration', 'file_size']
        
        for field in required_fields:
            if field not in metadata:
                return False, f"Video posts must include {field} in metadata"
        
        return True, None
    
    @staticmethod
    def _validate_article_post(data):
        """Validate article post specific requirements."""
        if not data.get('title'):
            return False, "Article posts must include a title"
        
        return True, None
    
    @staticmethod
    def _validate_poll_post(data):
        """Validate poll post specific requirements."""
        if not data.get('content'):
            return False, "Poll posts must include question content"
        
        return True, None
