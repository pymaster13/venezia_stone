import requests, time

from django.core.management.base import BaseCommand

from View1C.models import Materials

class Command(BaseCommand):
    help = 'Start restore database'

    def handle(self, *args, **options):

        ## ADD MATERIALS IN DATABASE ###
        start_time = time.time()
        materials_in_db = Materials.objects.all()
        resp = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/Materials', data={}, auth=('', ''))
