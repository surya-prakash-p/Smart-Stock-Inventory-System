from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Create admin automatically"

    def handle(self, *args, **kwargs):
        username = "admin"
        email = "admin@gmail.com"
        password = "admin123"

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            print("Admin created successfully")
        else:
            print("Admin already exists")