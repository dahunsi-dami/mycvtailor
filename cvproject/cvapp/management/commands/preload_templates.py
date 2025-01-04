from django.core.management.base import BaseCommand
from django.template.loader import get_template

class Command(BaseCommand):
    help = 'Preloads templates into memory'

    def handle(self, *args, **options):
        templates = [
            'registration/login.html',
            'main/home.html',
            'main/base.html',
            'registration/signup.html',
        ]
        
        for template_name in templates:
            try:
                get_template(template_name)
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully preloaded {template_name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to preload {template_name}: {e}')
                )
