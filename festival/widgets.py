from datetime import date

from . import models


class Widget:
    def __init__(self, template_name=None, get_context_data=None, short_name=None, name=None):
        if template_name is not None:
            self.template_name = template_name
        if get_context_data is not None:
            self.get_context_data = get_context_data
        if short_name is not None:
            self.short_name = short_name
        if name is not None:
            self.name = name

    template_name = None
    get_context_data = None
    short_name = None
    name = None

    @classmethod
    def get_choices(cls):
        # choices = tuple()
        # for sub_cls in cls.__subclasses__():
        #     choices = (*choices, (sub_cls.short_name, sub_cls.get_name()))
        # return choices
        choices = [(sub_cls.short_name, sub_cls.get_name()) for sub_cls in cls.__subclasses__()]
        return tuple(choices)

    @classmethod
    def get_class(cls, short_name):
        for sub_cls in cls.__subclasses__():
            if sub_cls.short_name == short_name:
                return sub_cls

    @classmethod
    def get_name(cls):
        if cls.name:
            return cls.name
        return cls.__class__.__name__


class SponsorWidget(Widget):
    name = 'Sponzoři'
    short_name = 's'
    template_name = 'festival/widgets/sponsor.html'

    def get_context_data(self):
        context_data = {
            'object_list': models.Sponsor.objects.filter(year__in=[models.Year.get_current()])
        }
        return context_data


class ContactWidget(Widget):
    name = 'Kontakty'
    short_name = 'c'
    template_name = 'festival/widgets/contact.html'

    def get_context_data(self):
        context_data = {
            'object_list': models.Contact.objects.filter(published=True)
        }
        return context_data


class PressReleaseWidget(Widget):
    name = 'Tiskovky'
    short_name = 'p'
    template_name = 'festival/widgets/press_release.html'

    def get_context_data(self):
        context_data = {
            'object_list': models.PressRelease.objects.filter(date_release__lte=date.today(), year__in=[models.Year.get_current()])
        }
        return context_data
