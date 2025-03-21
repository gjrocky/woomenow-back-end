import logging

from django.core.management import call_command
from django.core.management.base import BaseCommand
from wagtail.models import Page, Site, Locale, Collection

from .helper import create_data

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Closes the specified poll for voting and creates a Wagtail root page and default site"

    def handle(self, *args, **options):
        call_command('flush', interactive=False)
        logger.info('Flushed Database')
        logger.info(
            '---------------------------------------------------------------------------------------------------')

        logger.info('Creating Static data/Pages')

        # Check if a default locale exists
        if not Locale.objects.exists():
            default_locale = Locale.objects.create(language_code="en")  # Change "en" if needed
            print("✅ Default locale created:", default_locale)
        else:
            print("✅ Locale already exists!")

        # Ensure the site exists
        if not Page.objects.exists():
            root_page = Page.add_root(title="Root", slug="root")

            try:
                site = Site.objects.first()
                if not site:
                    Site.objects.create(root_page=root_page, hostname="localhost", port=8000, is_default_site=True)
                    print("Wagtail site created!")
            except Site.DoesNotExist:
                Site.objects.create(root_page=root_page, hostname="localhost", port=8000, is_default_site=True)

            # Ensure the root page has a locale assigned
            if not root_page.locale_id:
                root_page.locale = Locale.get_default()
                root_page.save()
                print("Locale assigned to root page.")

        if not Collection.get_first_root_node():
            Collection.add_root(name="Root Collection")
            print("Root collection created successfully!")
        else:
            print("Root collection already exists.")

        create_data()
        logger.info('Static data/Pages Created')
