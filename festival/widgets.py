from datetime import date

from . import models


class Widget:
    template_name = None
    get_context_data = None
    short_name = None
    name = None
    is_wrapper = False

    @classmethod
    def get_choices(cls):
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

    @classmethod
    def template_name_before(cls):
        return cls.template_name.replace('.html', '_before.html') if cls.is_wrapper else None

    @classmethod
    def template_name_after(cls):
        return cls.template_name.replace('.html', '_after.html') if cls.is_wrapper else None



class SponsorWidget(Widget):
    name = 'Sponzoři'
    short_name = 's'
    template_name = 'festival/widgets/sponsor.html'

    def get_context_data(self):
        context_data = {
            'object_list': models.Sponsor.objects.filter(year__in=[models.Year.get_current()]).order_by('category')
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
        today = date.today()
        context_data = {
            'object_list': models.PressRelease.objects.filter(date_release__lte=today,
                                                              date_release__year__in=[today.year, today.year-1])
        }
        return context_data


class FilmRegistrationWidget(Widget):
    name = 'Přihlášení filmu'
    short_name = 'f'
    template_name = 'festival/widgets/film_registration.html'

    def get_context_data(self):
        context_data = {
            'form': models.FilmRegistrationForm()
        }
        for field in context_data['form']:
            field.boolean = True if field.field.__class__.__name__ == 'BooleanField' else False
        return context_data


class GalleryBarWidget(Widget):
    name = 'odkaz do galerie'
    short_name = 'g'
    template_name = 'festival/widgets/gallery_bar.html'
    is_wrapper = True

    def get_context_data(self):
        return {}