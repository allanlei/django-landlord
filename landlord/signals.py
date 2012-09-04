from django.dispatch import Signal


landlord_init = Signal(providing_args=['thread'])

residence_init = Signal(providing_args=[])

tenant_created = Signal(providing_args=['instance'])



# landlord_created = Signal(providing_args=[])
# landlord_pre_change = Signal(providing_args=['instance'])
# landlord_changed = Signal(providing_args=['instance', 'changed', 'landlord'])
# landlord_tenant_prelookup = Signal(providing_args=[])


# landlord_current_tenant_pre_change = Signal(providing_args=['tenant'])
# landlord_current_tenant_changed = Signal(providing_args=['tenant'])


# tenant_created = Signal(providing_args=[])
# tenant_deleted = Signal(providing_args=[])