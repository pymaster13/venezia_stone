import requests, json
import kronos

from django.core.management.base import BaseCommand

from Account.models import User
from View1C.models import Project


@kronos.register('* * * * *')
class Command(BaseCommand):
    help = 'Start restore users'

    def handle(self, *args, **options):
        resp = requests.get('https://1c.veneziastone.com/trade_progr08/hs/VeneziaSkladOnline/getUserPermissions', data={}, auth=('', ''))

        if resp.status_code == 200:

            json_data = json.loads(resp.text)
            users = User.objects.values_list('email', flat=True)

            for user_project in json_data['prjs']:

                if user_project['id'] in users:

                    user = User.objects.get(email = user_project['id'])

                    project = Project.objects.get_or_create(name = user_project['project'], \
                    reserve = user_project['reserve'], stock = user_project['stock'],\
                    prices = user_project['prices'])[0]

                    if user_project['project'] == 'Venezia':
                        user.Venezia = project

                    elif user_project['project'] == 'Quartz':
                        user.Quartz = project

                    elif user_project['project'] == 'Charme':
                        user.Charme = project

                    user.save()
