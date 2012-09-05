# python manage.py landlord "syncdb --database" --tenant example.com

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from optparse import make_option

# Cannot run the following commands with this:
# Commands that support multidb should not be run with this command,
 # instead run command normally but with --database TENANT
# syncdb -> python manage.py syncdb --database TENANT

print 'Only use this command if the target command does not support multidb(--database)'

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--tenant',
            action='store',
            dest='tenant',
            default=None,
            help='Tenant to perform command on'),
        make_option('--use-flag',
            action='store_true',
            dest='flag',
            default=False,
            help='Appends --database instead of changing Tenant context'),
        )

    def handle(self, command, **options):
        from landlord import residence

        #Properply split command
        cmd, args, kwargs = 'createsuperuser', (), {}

        if options['flag']:
            kwargs.setdefault('database', options['tenant'])
            call_command(cmd, *args, **kwargs)
        else:
            with residence.get(**{'name': options['tenant']}):
                call_command(cmd, *args, **kwargs)