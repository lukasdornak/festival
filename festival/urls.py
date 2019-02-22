from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from django.utils.translation import gettext_lazy as _

admin.site.site_header = 'festivalkratasy.cz'

from . import views

app_name = 'festival'
urlpatterns = [
    path('', views.HomeTemplateView.as_view()),
    path(_('tvurce/') ,views.SectionListView.as_view(), {'role':'a'}, name='a'),
    path(_('navstevnik/'), views.SectionListView.as_view(), {'role':'b'}, name='b'),
    path(_('novinar/'), views.SectionListView.as_view(), {'role':'c'}, name='c'),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
