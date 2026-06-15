"""
Management command to inspect BestBrokersList objects.
Usage: python manage.py check_best_brokers
"""
import sys
from django.core.management.base import BaseCommand
from best_brokers.models import BestBrokersList


class Command(BaseCommand):
    help = 'Inspect BestBrokersList objects for [brokers_list] shortcode'

    def handle(self, *args, **options):
        sys.stdout.reconfigure(encoding='utf-8')
        SHORTCODE = '[brokers_list]'
        objs = BestBrokersList.objects.all()
        self.stdout.write(f"Total BestBrokersList objects: {objs.count()}\n")
        for obj in objs:
            content = obj.content or ''
            has_shortcode = SHORTCODE in content
            num_selected = obj.selected_brokers.count()
            self.stdout.write(
                f"id={obj.id}  slug={obj.slug}\n"
                f"  has [brokers_list]: {has_shortcode}\n"
                f"  selected_brokers count: {num_selected}\n"
                f"  content[:300]: {content[:300]!r}\n\n"
            )
