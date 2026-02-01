"""
ASGI config for zombicide_editor project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zombicide_editor.settings')

application = get_asgi_application()
