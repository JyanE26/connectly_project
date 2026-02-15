from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType
from posts.models import Post, Comment


class Command(BaseCommand):
    help = 'Create default groups and assign permissions'

    def handle(self, *args, **options):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name='Admin')
        user_group, created = Group.objects.get_or_create(name='User')
        moderator_group, created = Group.objects.get_or_create(name='Moderator')

        # Get content types
        post_content_type = ContentType.objects.get_for_model(Post)
        comment_content_type = ContentType.objects.get_for_model(Comment)
        user_content_type = ContentType.objects.get_for_model(User)

        # Get permissions
        post_permissions = Permission.objects.filter(content_type=post_content_type)
        comment_permissions = Permission.objects.filter(content_type=comment_content_type)
        user_permissions = Permission.objects.filter(content_type=user_content_type)

        # Assign permissions to Admin group (all permissions)
        admin_group.permissions.set(post_permissions | comment_permissions | user_permissions)

        # Assign limited permissions to User group
        user_permissions = Permission.objects.filter(
            codename__in=['add_post', 'change_post', 'delete_post', 'add_comment', 'change_comment']
        )
        user_group.permissions.set(user_permissions)

        # Assign moderate permissions to Moderator group
        moderator_permissions = Permission.objects.filter(
            codename__in=['change_post', 'delete_post', 'change_comment', 'delete_comment']
        )
        moderator_group.permissions.set(moderator_permissions)

        self.stdout.write(self.style.SUCCESS('Successfully created groups and assigned permissions'))

        # Create an admin user for testing
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@example.com'}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))
        else:
            admin_user.groups.add(admin_group)
            self.stdout.write(self.style.SUCCESS('Added admin user to Admin group'))
