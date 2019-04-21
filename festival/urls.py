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
    path(_('dekujeme-za-registraci-filmu/'), views.ThanksView.as_view(), {'for': 'f'}),
    path(_('dekujeme-za-zakoupeni-vstupenek/'), views.ThanksView.as_view(), {'for': 't'}),
    path(_('zaplatit-registraci/<int:pk>/<slug:film_name>/'), views.AlterPayFilmRegistrationView.as_view()),
    path(_('opakovat-platbu/<int:pk>/'), views.RepeatPaymentView.as_view()),
    path(_('podminky-prihlaseni/'), views.TextView.as_view(), {'text': 'tor'}),
    path(_('zasady-zpracovani-osobnich-udaju/'), views.TextView.as_view(), {'text': 'gdpr'}),
    path('thepay-payment-done/', views.PaymentCreateView.as_view()),
    path('ajax/film-registration/', views.FilmRegistrationView.as_view()),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
