from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    POST_TYPES = {
        'text': 'Standard text post',
        'image': 'Post with image attachment',
        'video': 'Post with video attachment',
        'article': 'Long-form article post',
        'poll': 'Interactive poll post'
    }
    
    content = models.TextField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    post_type = models.CharField(max_length=20, choices=POST_TYPES, default='text')
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"


class Like(models.Model):
    """
    Model for tracking user likes on posts
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensure a user can only like a post once
        unique_together = ('user', 'post')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"
