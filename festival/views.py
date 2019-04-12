from django.http import Http404
from django.shortcuts import redirect, reverse
from django.views.generic import ListView, TemplateView, UpdateView, CreateView
from django.utils.translation import gettext_lazy as _

from . import models, the_pay

class HomeTemplateView(TemplateView):
    template_name = 'festival/home.html'

    def get(self, request, *args, **kwargs):
        role = request.session.get('FESTIVAL_ROLE', None)
        if role:
            return redirect(reverse(role))
        self.first_time = True
        self.nav = bool(request.GET.get('nav', 0))
        if request.user.is_staff:
            self.all_sections = models.Section.objects.all()
        else:
            self.all_sections = models.Section.objects.filter(published=True)
        return super().get(request, *args, **kwargs)


class SectionListView(ListView):
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
        self.object_id = request.session.get('UNPAID_FILM_REGISTERED')
        return super().dispatch(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if self.object_id:
            return models.Film.objects.get(id=self.object_id)
        return None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        for field in context_data['form']:
            field.boolean = True if field.field.__class__.__name__ == 'BooleanField' else False
        return context_data

    def form_valid(self, form):
        self.object = form.save()
        self.request.session['UNPAID_FILM_REGISTERED'] = self.object.id
        return self.redirect_to_pay()

    def redirect_to_pay(self):
        section = models.Section.objects.filter(widget='f').first()
        hash_for_back_to_eshop_url = section.slug_en if self.request.LANGUAGE_CODE == 'en' else section.slug
        payment = the_pay.Payment(
            value=float(100),
            description='registrační poplatek',
            return_url=f"http://{ self.request.META['HTTP_HOST'] }/thepay-payment-done/",
            merchant_data=f'{{"f":{ self.object.id }}}',
            back_to_eshop_url=f"http://{ self.request.META['HTTP_HOST'] }/{ _('tvurce') }/#{ hash_for_back_to_eshop_url }"
        )
        helper = the_pay.DivHelper(payment=payment)
        self.template_name = self.pay_template_name
        return self.render_to_response(context=helper.get_context())


class ThanksView(TemplateView):
    template_names = {
        'f': 'festival/film_registration_paid.html',
        't': 'festival/tickets_paid.html',
    }

    def get(self, request, *args, **kwargs):
        self.payment = request.session.get('THEPAY_PAYMENT')
        if self.payment is None:
            raise Http404("Page not found")
        thanks_for = kwargs['for']
        self.template_name = self.template_names[thanks_for]
        return super().get(request, *args, thanks_for=thanks_for, **kwargs)

    def get_context_data(self, thanks_for, **kwargs):
        context_data = super().get_context_data(**kwargs)
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
            'film': payment.get_film_id(request),
            'tickets': payment.get_ticket_ids(request),
            'type': payment.get_type(),
        }
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
        form.fields['ticket'].disabled = True
        form.fields['type'].disabled = True
        return form

    def get_success_url(self):
        return self.success_urls[self.object.type]
