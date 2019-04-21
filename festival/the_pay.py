import time, json

from hashlib import md5
from urllib.parse import urlencode
from django.conf import settings


class PaymentMixin:
    eet_dph = {}
    params = {}

    def get_params(self):
        params = {k: v for k, v in self.params.items() if v is not None}
        if params.get('deposit') is not None:
            params['deposit'] = 1 if params['deposit'] else 0
        if params.get('isRecurring') is not None:
            params['isRecurring'] = 1 if params['isRecurring'] else 0
        if self.eet_dph:
            params.update(self.eet_dph)
        return params

    def get_signed_params(self):
        params = self.get_params()
        qs = ''
        for k, v in params.items():
            qs += f'{ k }={ v }&'
        qs += f'password={ settings.TP_PASSWORD }'
        params['signature'] = md5(qs.encode('utf-8')).hexdigest()
        return params


class Payment(PaymentMixin):
    def __init__(self,
                 value=None,
                 currency=None,
                 description=None,
                 merchant_data=None,
                 customer_email=None,
                 return_url=None,
                 back_to_eshop_url=None,
                 merchant_specific_symbol=None,
                 specific_symbol=None,
                 deposit=None,
                 is_recurring=None,
                 eet_dph={},
                 ):
        self.params = {
            'merchantId' : settings.TP_MERCHANT_ID,
            'accountId' : settings.TP_ACCOUNT_ID,
            'value': value,
            'currency': currency,
            'description': description,
            'merchantData': merchant_data,
            'customerEmail': customer_email,
            'returnUrl': return_url,
            'backToEshopUrl': back_to_eshop_url,
            'merchantSpecificSymbol': merchant_specific_symbol,
            'specificSymbol': specific_symbol,
            'deposit': deposit,
            'isRecurring': is_recurring}
        self.eet_dph = eet_dph

    def get_params(self):
        params = super().get_params()
        params['value'] = self.clean_value(params['value'])
        return params

    def clean_value(self, value):
        value = float(value)
        if value <= 0:
            raise ValueError('Value must be positive.')
        return f'{value:.2f}'


class ReturnedPayment(PaymentMixin):
    def __init__(self, GET):
        self.params = {
            'merchantId': GET.get('merchantId'),
            'accountId': GET.get('accountId'),
            'value': GET.get('value'),
            'currency': GET.get('currency'),
            'methodId': GET.get('methodId'),
            'description': GET.get('description'),
            'merchantData': GET.get('merchantData'),
            'status': GET.get('status'),
            'paymentId': GET.get('paymentId'),
            'ipRating':GET.get('ipRating'),
            'isOffline': GET.get('isOffline'),
            'needConfirm': GET.get('needConfirm'),
            'isConfirm': GET.get('isConfirm'),
            'customerAccountNumber': GET.get('customerAccountNumber'),
            'customerAccountName': GET.get('customerAccountName'),}
        self.signature = GET.get('signature')
        self.data = json.loads(self.params['merchantData'])

    signature = None
    data = {}

    def signature_is_valid(self):
        signature = self.get_signed_params().get('signature')
        if self.signature and self.signature == signature:
            return True
        return False

    def get_type(self):
        return list(self.data.keys())[0]

    def to_JSON(self):
        return {'params': self.params, 'data': self.data}


class AbstractHelper:
    def __init__(self, payment):
        self.payment = payment

    payment = None
    context = {}

    def get_context(self):
        context = self.context
        context.update({
            'query_string': self.get_query_string(),
        })
        return context

    def get_query_string(self, **kwargs):
        params = self.payment.get_signed_params()
        params.update(kwargs)
        return urlencode(params)


class DivHelper(AbstractHelper):
    def __init__(self, payment,
                 gate_url=settings.TP_GATE_URL,
                 skin=None,
                 disable_button_css=False,
                 disable_popup_css=False):
        super().__init__(payment)
        self.context.update({
            'gate_url': gate_url,
            'skin': skin,
            'disable_button_css': disable_button_css,
            'disable_popup_css': disable_popup_css,
            'time': int(time.time()),
        })

    context = {
        'helper_template_name': 'festival/helpers/tp_div_helper.html'
    }

    def get_query_string(self):
        helper_params = {
            'disableButtonCss': str(self.context['disable_button_css']).lower(),
            'disablePopupCss': str(self.context['disable_popup_css']).lower(),
        }
        return super().get_query_string(**helper_params)
