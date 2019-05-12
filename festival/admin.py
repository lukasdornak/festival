import base64
from io import BytesIO

from django.contrib import admin, messages
from django.core.files.uploadedfile import InMemoryUploadedFile

from import_export.admin import ImportExportModelAdmin

from . import models, forms


def make_assign_to_gallery(year):
    def assign_to_gallery(modeladmin, request, queryset):
        for photo in queryset:
            changed = photo.assign_to(year)
            if changed:
                messages.info(request, f'Fotka { photo.name } zařazena do galerie { year }')

    assign_to_gallery.short_description = f'Zařadit do galerie { year }'
    assign_to_gallery.__name__ = f'assign_to_gallery_{ year.id }'

    return assign_to_gallery


class PublishMixin:
    actions = ['publish', 'hide']

    def publish(self, request, queryset):
        queryset.update(published=True)

    def hide(self, request, queryset):
        queryset.update(published=False)

    publish.short_description = 'Publikovat'
    hide.short_description = 'Skrýt'


@admin.register(models.Year)
class YearAdmin(admin.ModelAdmin):
    model = models.Year
    list_display = ['__str__', 'vol', 'name', 'date_start', 'date_end', 'current']


@admin.register(models.Article)
class ArticleAdmin(PublishMixin, admin.ModelAdmin):
    model = models.Article


@admin.register(models.Section)
class SectionAdmin(PublishMixin, admin.ModelAdmin):
    model = models.Section
    list_display = ['__str__', 'role', 'order', 'published']
    list_filter = ['role', 'published']
    fieldsets = (
        (None, {
            'fields': ('published', 'headline', 'headline_en', 'role', 'order'),
        }),
        ('obsah', {
            'fields': ('full_text', 'full_text_en', 'extra_full_text', 'extra_full_text_en')
        }),
        ('vlastnosti', {
            'fields': ('auto_headline', 'max_columns', 'widget', 'widget_first' )
        })
    )


@admin.register(models.Guide)
class GuideAdmin(admin.ModelAdmin):
    model = models.Guide


class PhotoInline(admin.TabularInline):
    model = models.Photo
    fields = ['original', 'description', 'order']
    extra = 1


@admin.register(models.Gallery)
class GalleryAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, ]
    form = forms.GalleryAdminForm

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        photo_list = dict(form.files).get('photo_list', [])
        for photo in photo_list:
            models.Photo.objects.create(original=photo, description=obj.get_year(), year=obj)


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ['id', '__str__', 'year', 'order']
    list_display_links = ['__str__']
    list_filter = ['year']
    form = forms.PhotoAdminForm
    actions = ['unassign']
    readonly_fields = ['get_img_url']

    def get_img_url(self, obj):
        return obj.original.url

    get_img_url.short_description = "url fotky"

    def unassign(self, request, queryset):
        for photo in queryset:
            if photo.year:
                messages.info(request, f'Fotka { photo } vyřazena z galerie { photo.year }')
        queryset.update(year=None)

    unassign.short_description = "Vyřadit z galerie"

    def get_actions(self, request):
        actions = super().get_actions(request)

        for year in list(models.Year.objects.all()):
            action = make_assign_to_gallery(year)
            actions[action.__name__] = (action, action.__name__, action.short_description)

        return actions

    def save_model(self, request, obj, form, change):
        if 'cropped' in form.changed_data:
            format, imgstr = request.POST['cropped'].split(';base64,')
            ext = format.split('/')[-1]
            file = BytesIO(base64.b64decode(imgstr))
            image = InMemoryUploadedFile(file,
                                         field_name='cropped',
                                         name=str(obj.id) + ext,
                                         content_type="image/jpeg",
                                         size=len(file.getvalue()),
                                         charset=None)
            obj.cropped = image
        super().save_model(request, obj, form, change)

    class Media:
        js = ['https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js',
              'https://cdnjs.cloudflare.com/ajax/libs/croppie/2.6.1/croppie.min.js',
              '/static/festival/js/croppie_image_field.js']
        css = {
            'all': ('https://cdnjs.cloudflare.com/ajax/libs/croppie/2.6.1/croppie.min.css',)
        }


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    model = models.Contact


@admin.register(models.Film)
class FilmAdmin(ImportExportModelAdmin):
    model = models.Film
    list_display = ['__str__', 'year', 'time', 'category', 'genre', 'country', 'get_rating', 'status', 'technical_check']
    list_filter = ['status', 'category', 'genre']


@admin.register(models.Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    model = models.Evaluation
    readonly_fields = ['user']
    list_display = ['__str__', 'user', 'film', 'like', 'verbal', 'technical']
    list_filter = ['film', 'user', 'technical']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj is not None:
            return request.user == obj.user or request.user.is_superuser
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            return request.user == obj.user or request.user.is_superuser
        return super().has_change_permission(request, obj)


@admin.register(models.Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    model = models.Sponsor
    list_display = ['name', 'category', 'order', 'url']
    list_editable = ['order']
    list_filter = ['category', 'year']


@admin.register(models.PressRelease)
class PressRelease(admin.ModelAdmin):
    models = models.PressRelease
    list_display = ['__str__', 'date_release', 'year']
    list_filter = ['year']


@admin.register(models.ThepayPayment)
class ThepayPaymentAdmin(admin.ModelAdmin):
    model = models.ThepayPayment
    list_display = ['__str__', 'datetime', 'type', 'film', 'value', 'status', 'status_ok', 'valid_signature']
    list_filter = ['type', 'status', 'datetime']

    def status_ok(self, obj=None):
        return obj.status not in [models.ThepayPayment.CANCELED, models.ThepayPayment.ERROR]

    status_ok.short_description = 'status ok'
    status_ok.boolean = True


@admin.register(models.Texts)
class TextsAdmin(admin.ModelAdmin):
    model = models.Texts
    fieldsets = (
        (None, {
            'fields': ('default_from_email', )
        }),
        ('sdílení', {
            'fields': ('og_title', 'og_title_en', 'og_description', 'og_description_en', 'og_image'),
            'classes': ('collapse',),
        }),
        ('výber platební metody', {
            'fields': ('method_select_film', 'method_select_film_en', 'method_select_tickets', 'method_select_tickets_en'),
            'classes': ('collapse',),
        }),
        ('podmínky přihlášení', {
            'fields': ('tor', 'tor_en'),
            'classes': ('collapse',),
        }),
        ('zásady zpracování osobních údajů', {
            'fields': ('gdpr', 'gdpr_en'),
            'classes': ('collapse',),
        }),
        ('email: film byl zaregistrován, ale zatím ještě nebyl uhrazen poplatek', {
            'fields': ('mail_film_registered_unpaid_subject', 'mail_film_registered_unpaid_subject_en',
                       'mail_film_registered_unpaid_message', 'mail_film_registered_unpaid_message_en',
                       'mail_film_registered_unpaid_message_html', 'mail_film_registered_unpaid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: registrační poplatek byl úspěšně zaplacen', {
            'fields': ('mail_film_paid_subject', 'mail_film_paid_subject_en',
                       'mail_film_paid_message', 'mail_film_paid_message_en',
                       'mail_film_paid_message_html', 'mail_film_paid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: registrační poplatek se nepodařilo zaplatit', {
            'fields': ('mail_film_unpaid_subject', 'mail_film_unpaid_subject_en',
                       'mail_film_unpaid_message', 'mail_film_unpaid_message_en',
                       'mail_film_unpaid_message_html', 'mail_film_unpaid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: registrační poplatek stále nebyl zaplacen', {
            'fields': ('mail_film_still_unpaid_subject', 'mail_film_still_unpaid_subject_en',
                       'mail_film_still_unpaid_message', 'mail_film_still_unpaid_message_en',
                       'mail_film_still_unpaid_message_html', 'mail_film_still_unpaid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: vstupenky jsou rezervovány, ale ještě nebyly zaplaceny', {
            'fields': ('mail_tickets_reserved_unpaid_subject', 'mail_tickets_reserved_unpaid_subject_en',
                       'mail_tickets_reserved_unpaid_message', 'mail_tickets_reserved_unpaid_message_en',
                       'mail_tickets_reserved_unpaid_message_html', 'mail_tickets_reserved_unpaid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: vstupenky byly úspěšně zaplaceny', {
            'fields': ('mail_tickets_paid_subject', 'mail_tickets_paid_subject_en',
                       'mail_tickets_paid_message', 'mail_tickets_paid_message_en',
                       'mail_tickets_paid_message_html', 'mail_tickets_paid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: vstupenky se nepodařilo zaplatit', {
            'fields': ('mail_tickets_unpaid_subject', 'mail_tickets_unpaid_subject_en',
                       'mail_tickets_unpaid_message', 'mail_tickets_unpaid_message_en',
                       'mail_tickets_unpaid_message_html', 'mail_tickets_unpaid_message_html_en'),
            'classes': ('collapse',),
        }),
        ('email: vstupenky doposud nebyly zaplaceny a proto již nejsou déle rezervovány', {
            'fields': ('mail_tickets_still_unpaid_subject', 'mail_tickets_still_unpaid_subject_en',
                       'mail_tickets_still_unpaid_message', 'mail_tickets_still_unpaid_message_en',
                       'mail_tickets_still_unpaid_message_html', 'mail_tickets_still_unpaid_message_html_en'),
            'classes': ('collapse',),
        }),
    )

@admin.register(models.Email)
class EmailModelAdmin(admin.ModelAdmin):
    models = models.Email
    list_display = ['datetime', 'subject', 'message', 'recipient_list', ]
