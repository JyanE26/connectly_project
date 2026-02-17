from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from singletons.config_manager import ConfigManager


class ConfigView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get current configuration settings"""
        config = ConfigManager()
        all_settings = config.get_all_settings()
        
        return Response({
            'message': 'Current configuration settings',
            'settings': all_settings,
            'description': {
                'DEFAULT_PAGE_SIZE': 'Number of posts per page',
                'ENABLE_ANALYTICS': 'Whether analytics logging is enabled',
                'RATE_LIMIT': 'Maximum requests per hour per user'
            }
        })

    def post(self, request):
        """Update configuration settings (admin only)"""
        # Check if user is admin (simplified check)
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        config = ConfigManager()
        new_settings = request.data.get('settings', {})
        
        # Update settings
        for key, value in new_settings.items():
            if key in config.get_all_settings():
                config.set_setting(key, value)
        
        return Response({
            'message': 'Configuration updated successfully',
            'updated_settings': new_settings,
            'current_settings': config.get_all_settings()
        })

    def delete(self, request):
        """Reset configuration to defaults (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        config = ConfigManager()
        config.reset_to_defaults()
        
        return Response({
            'message': 'Configuration reset to defaults',
            'default_settings': config.get_all_settings()
        })
