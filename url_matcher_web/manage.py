#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_matcher_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # Create necessary directories for media files
    import os
    
    # This code will run before executing any management commands
    try:
        # Import settings to get MEDIA_ROOT and URL_MATCHER_OUTPUT_DIR
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'url_matcher_project.settings')
        import django
        django.setup()
        
        from django.conf import settings
        
        # Create media directories if they don't exist
        media_root = settings.MEDIA_ROOT
        url_matcher_output_dir = settings.URL_MATCHER_OUTPUT_DIR
        csv_uploads_dir = os.path.join(media_root, 'csv_uploads')
        
        for directory in [media_root, url_matcher_output_dir, csv_uploads_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Created directory: {directory}")
    except Exception as e:
        print(f"Error creating directories: {e}")
    
    # Continue with normal Django management commands
    main()
