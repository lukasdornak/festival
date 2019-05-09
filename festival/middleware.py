import re
from django.utils import translation


class FestivalLocaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    en_urls = [re.compile(p) for p in [
        '^/author/',
        '^/visitor/',
        '^/journalist/',
        '^/gallery/',
        '^/thanks-for-film-registration/',
        '^/thanks-for-tickets-purchase/',
        '^/repeat-payment/',
        '^/terms-of-registration/',
        '^/privacy-policy/',
    ]]
    cs_urls = [re.compile(p) for p in [
        '^/tvurce/',
        '^/navstevnik/',
        '^/novinar/',
        '^/galerie/',
        '^/dekujeme-za-registraci-filmu/',
        '^/dekujeme-za-zakoupeni-vstupenek/',
        '^/opakovat-platbu/',
        '^/podminky-prihlaseni/',
        '^/zasady-zpracovani-osobnich-udaju/',
    ]]

    def get_lang_from_url(self, request):
        for url in self.en_urls:
            if url.search(request.path_info):
                return 'en'
        for url in self.cs_urls:
            if url.search(request.path_info):
                return 'cs'
        return None

    def __call__(self, request):
        language_from_url = self.get_lang_from_url(request)
        if language_from_url:
            request.session['LANGUAGE_SESSION_KEY'] = language_from_url
            translation.activate(language_from_url)
        else:
            language_from_request = translation.get_language_from_request(request, check_path=False)
            translation.activate(language_from_request)
        request.LANGUAGE_CODE = translation.get_language()
        response = self.get_response(request)
        if language_from_url:
            response.set_cookie('django_language', language_from_url)
        return response