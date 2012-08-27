from django.dispatch import Signal

landlord_initized = Signal(providing_args=['thread'])

namespace_added = Signal(providing_args=['namespace'])
namespace_removed = Signal(providing_args=['namespace'])
namespace_changed = Signal(providing_args=['namespace', 'from_namespace'])
namespace_peaked = Signal(providing_args=['namespace'])