import json

from django.http import Http404
from django.shortcuts import redirect, reverse
from django.views.generic import CreateView, DetailView, ListView, TemplateView, UpdateView
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from . import models, the_pay


class NavContextMixin:
    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['nav_on'] = bool(self.request.GET.get('nav', 0))
        if self.request.user.is_staff:
            context_data['nav_sections'] = models.Section.objects.all()
        else:
            context_data['nav_sections'] = models.Section.objects.filter(published=True)
        return context_data


class HomeTemplateView(NavContextMixin, TemplateView):
    template_name = 'festival/home.html'

    def get(self, request, *args, **kwargs):
        role = request.session.get('FESTIVAL_ROLE', None)
        if role:
            return redirect(reverse(role))
        self.first_time = True
        return super().get(request, *args, **kwargs)


class SectionListView(NavContextMixin, ListView):
    model = models.Section

    def get_queryset(self):
        if self.request.user.is_staff:
            self.all_sections = models.Section.objects.all()
        else:
            self.all_sections = models.Section.objects.filter(published=True)
        return self.all_sections.filter(role=self.role)

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        for obj in self.object_list:
            if obj.widget:
                obj.widget_context = obj.get_widget().get_context_data(self)
        return context_data

    def get(self, request, *args, **kwargs):
        self.role = kwargs.get('role', None)
        if self.role:
            request.session['FESTIVAL_ROLE'] = self.role
        self.first_time = bool(request.GET.get('first', 0))
        self.nav = bool(request.GET.get('nav', 0))
        self.home = bool(request.GET.get('home', 0))
        return super().get(request, *args, **kwargs)


class FilmRegistrationView(UpdateView):
    success_url = "/tvurce/#prihlaseni-filmu"
    model = models.FilmRegistrationForm
    form_class = models.FilmRegistrationForm
    template_name = 'festival/forms/film_registration.html'
    pay_template_name = 'festival/pay_film_registration.html'
    object_id = None

    def dispatch(self, request, *args, **kwargs):
        self.object_id = request.session.get('UNPAID_FILM')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if self.object_id:
            return models.Film.objects.filter(id=self.object_id).first()
        return None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        for field in context_data['form']:
            field.boolean = True if field.field.__class__.__name__ == 'BooleanField' else False
        return context_data

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['UNPAID_FILM'] = self.object.id
        return self.redirect_to_pay()

    def redirect_to_pay(self):
        section = models.Section.objects.filter(widget='f').first()
        hash_for_back_to_eshop_url = section.slug_en if self.request.LANGUAGE_CODE == 'en' else section.slug
        payment = the_pay.Payment(
            value=float(100),
            description='registrační poplatek',
            return_url=f"https://{ self.request.META['HTTP_HOST'] }/thepay-payment-done/",
            merchant_data=f'{{"f":{ self.object.id }}}',
            back_to_eshop_url=f"https://{ self.request.META['HTTP_HOST'] }/{ _('tvurce') }/#{ hash_for_back_to_eshop_url }"
        )
        helper = the_pay.DivHelper(payment=payment)
        self.template_name = self.pay_template_name
        context = helper.get_context()
        context['texts'] = models.Texts.objects.first()
        return self.render_to_response(context)


class RepeatPaymentView(NavContextMixin, DetailView):
    model = models.ThepayPayment
    template_name = 'festival/repeat_payment.html'

    def get_object(self, queryset=None):
        payment_id = int(self.kwargs.get(self.pk_url_kwarg))
        obj = models.ThepayPayment.objects.filter(paymentId=payment_id).first()
        if obj is None:
            raise Http404(payment_id)
        if obj.status not in [
            models.ThepayPayment.CANCELED,
            models.ThepayPayment.ERROR,
            models.ThepayPayment.UNDERPAID]:
            raise Http404(_('Page no found'))
        film_id = json.loads(obj.merchantData).get('f')
        if film_id is not None and models.ThepayPayment.objects.filter(
                film_id=film_id, status__in=[models.ThepayPayment.OK,
                                             models.ThepayPayment.WAITING,
                                             models.ThepayPayment.CARD_DEPOSIT]).exists():
            raise Http404(_('Page no found'))
        return obj

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        payment = the_pay.Payment(
            value=float(100),
            description='registrační poplatek',
            return_url=f"https://{ self.request.META['HTTP_HOST'] }/thepay-payment-done/",
            merchant_data=self.object.merchantData,
            back_to_eshop_url=f"https://{ self.request.META['HTTP_HOST'] }{ _('/opakovat-platbu/') }{ self.object.paymentId }/"
        )
        helper = the_pay.DivHelper(payment=payment)
        context_data.update(**helper.get_context())
        return context_data


class AlterPayFilmRegistrationView(NavContextMixin, DetailView):
    model = models.Film
    template_name = 'festival/alter_pay_film_registration.html'

    def get_object(self, queryset=None):
        obj = super().get_object()
        if obj is None or obj.status != obj.UNPAID or slugify(obj.name) != self.kwargs.get('film_name'):
            raise Http404(_('Page not found'))
        return obj

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data()
        payment = the_pay.Payment(
            value=float(100),
            description='registrační poplatek',
            return_url=f"https://{ self.request.META['HTTP_HOST'] }/thepay-payment-done/",
            merchant_data=f'{{"f":{ self.object.id }}}',
            back_to_eshop_url=f"https://{ self.request.META['HTTP_HOST'] }{ _('/zaplatit-registraci/') }{ self.object.id }/{ slugify(self.object.name) }/"
        )
        helper = the_pay.DivHelper(payment=payment)
        context_data.update(**helper.get_context(), value=100)
        return context_data


class ThanksView(NavContextMixin, TemplateView):
    template_names = {
        'f': 'festival/film_registration_paid.html',
        't': 'festival/tickets_paid.html',
    }

    def get(self, request, *args, **kwargs):
        self.payment = request.session.get('THEPAY_PAYMENT')
        if self.payment is None:
            raise Http404(_('Page no found'))
        thanks_for = kwargs['for']
        self.template_name = self.template_names[thanks_for]
        return super().get(request, *args, thanks_for=thanks_for, **kwargs)

    def get_context_data(self, thanks_for, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data['status'] = int(self.payment['params']['status'])
        context_data['payment_id'] = int(self.payment['params']['paymentId'])
        if thanks_for == 'f':
            context_data['film'] = models.Film.objects.filter(id=self.payment['data'][thanks_for]).first()
        elif thanks_for == 't':
            context_data['tickets'] = models.Ticket.objects.filter(id__in=self.payment['data'][thanks_for])
        return context_data


class PaymentCreateView(CreateView):
    model = models.ThepayPayment
    form_class = models.ThepayPaymentForm
    success_urls = {
        'f': _('/dekujeme-za-registraci-filmu/'),
        't': _('/dekujeme-za-nakup-vstupenek/')
    }

    def get(self, request, *args, **kwargs):
        payment = the_pay.ReturnedPayment(request.GET)
        self.initial = {
            'valid_signature': payment.signature_is_valid(),
            'film': payment.data.get('f'),
            'tickets': payment.data.get('t'),
            'type': payment.get_type(),
        }
        if payment.params.get('status') not in [models.ThepayPayment.CANCELED, models.ThepayPayment.ERROR]:
            unpaid_id = request.session.get('UNPAID_FILM')
            if unpaid_id:
                if unpaid_id == self.initial['film']:
                    request.session.pop('UNPAID_FILM')
            else:
                unpaid_ids = request.session.get('UNPAID_TICKETS')
                if unpaid_ids and unpaid_ids == self.initial['tickets']:
                    request.session.pop('UNPAID_TICKETS')
        request.session['THEPAY_PAYMENT'] = payment.to_JSON()
        return self.post(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('GET',):
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['valid_signature'].disabled = True
        form.fields['film'].disabled = True
        form.fields['tickets'].disabled = True
        form.fields['type'].disabled = True
        return form

    def get_success_url(self):
        return self.success_urls[self.object.type]


class TextView(NavContextMixin, TemplateView):
    template_names = {
        'tor': 'festival/tor.html'
    }

    def get_context_data(self, **kwargs):
        self.text = kwargs.get('text')
        context_data = super().get_context_data(**kwargs)
        context_data['texts'] = models.Texts.objects.first()
        return context_data

    def get_template_names(self):
        return [self.template_names[self.text]]
