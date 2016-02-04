from waffle import Switch


class SwitchMixin(object):
    @classmethod
    def toggle_switch(cls, name, active):
        switch, _created = Switch.objects.get_or_create(name=name)
        switch.active = active
        switch.save()
