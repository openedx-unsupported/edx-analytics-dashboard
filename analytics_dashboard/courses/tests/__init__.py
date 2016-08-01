# Note: this is an undocumented way of toggling waffle switches and may break in future versions.
# This mixin class exists only for tests (for testing features with switches on and off). The documented way of toggling
# swtiches is to execute django management commands in the commandline.
# DELETED IN FUTURE PATCH
from waffle.models import Switch


class SwitchMixin(object):
    @classmethod
    def toggle_switch(cls, name, active):
        switch, _created = Switch.objects.get_or_create(name=name)
        switch.active = active
        switch.save()
