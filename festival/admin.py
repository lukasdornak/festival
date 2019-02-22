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


@admin.register(models.Article)
class ArticleAdmin(PublishMixin, admin.ModelAdmin):
    model = models.Article


@admin.register(models.Section)
class SectionAdmin(PublishMixin, admin.ModelAdmin):
    model = models.Section
    list_display = ['__str__', 'role', 'order', 'published']
    list_filter = ['role', 'published']


@admin.register(models.Guide)
class GuideAdmin(admin.ModelAdmin):
    model = models.Guide


@admin.register(models.Contact)
class ContactAdmin(admin.ModelAdmin):
    model = models.Contact


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    model = models.Category


@admin.register(models.Film)
class FilmAdmin(admin.ModelAdmin):
    model = models.Film
    list_display = ['name', 'year', 'author_name', 'category', 'author_state', 'get_rating']
    list_filter = ['category', 'author_state']

@admin.register(models.Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    model = models.Evaluation
    readonly_fields = ['user']

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
        super().save_model(request, obj, form, change)


@admin.register(models.Sponsor)
class SponsorAdmin(admin.ModelAdmin):
    model = models.Sponsor


@admin.register(models.PressRelease)
class PressRelease(admin.ModelAdmin):
    models = models.PressRelease