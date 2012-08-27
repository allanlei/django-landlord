from landlord import landlord

def landlord(request):
    return {
        'landlord': {
            'current': landlord.get_current_namespace(),
        }
    }