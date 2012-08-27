Purpose:
    * Router read/write for any data to a specific location depending on tenant
        - Models
            - Requires 'landlord.db.routers.LandlordRouter' installed into DATABASE_ROUTERS
            - settings.DATABASES
        - Cache - ???


Installation
    pip install django-landlord

Setup
    1. Add 'landlord' to INSTALLED_APPS
    2. Add 'landlord.db.routers.LandlordRouter' to DATABASE_ROUTERS for multitenant database functionality
    3. Add 'landlord.backends.ModelBackend'
    
    (Optional) Configure  function that gets passed (tenant, model, hints**)
            - LANDLORD_ROUTER_READ_HANDLER
            - LANDLORD_ROUTER_WRITE_HANDLER
            - LANDLORD_ROUTER_ALLOW_RELATION_HANDLER
            - LANDLORD_ROUTER_ALLOW_SYNCDB_HANDLER
Configuration

Usage
* Function block
    tenant = residence['tenant_identifier']
    
    with tenant:
        User.objects.all()

    or

    with residence.find_tenant('...'):
        User.objects.all()

* Request cycle
    Install 'landlord.middleware.LandlordMiddleware' before any middleware that needs to be routed
    
    User.objects.all()

* 3rd party commands ie syncdb, migrate, etc, uses function block method wrapped around the desired command
    - Could solve django-south's db caching problem since no part of south is loaded yet, 
    compared to overriding syncdb, migrate, etc

    with residence.find_tenant('..'):
        call_command('...')

    python manage.py landlord "syncdb -v -qwee" --tenant example.com

    python manage.py syncdb -v --noinput
    heroku run "python manage.py landlord 'syncdb -v --noinput' --tenant example.com --residence default"


Common Scenarios
## 1 Database, N schemas, 1 database connection
    @receiver(current_tenant_changed)
        def switch_schema(sender, tenant, **kwargs):
            cursor = connections['default'].cursor()
            cursor.execute('...')
            
## N Databases, 1 schema, N database connections
    - Set LANDLORD_DB_CONTROLLER = True

## 1 Database, N schemas, N database connections
    - Set LANDLORD_DB_CONTROLLER = True

* N DB, 1 schema, N connections ~= 1 DB, N schemas, N connections
    - Have each database in settings.DATABASES point to the same database server
    - Use django-dbconnect to switch schemas based on alias, username, etc...



Django's generic views do not work if the same queryset is being executed for the same tenant.
My guess would be that this is related to how Django caches its querysets if run more than once.
Running {{ object_list }} for the first tenant is fine, but additional calls to {{ object_list }}
will result in tenant #1's results as the queryset has been resolved already.