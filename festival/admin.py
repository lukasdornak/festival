from django.contrib import admin

from . import models


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


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    model = models.Contact


@admin.register(models.Film)
class FilmAdmin(admin.ModelAdmin):
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
