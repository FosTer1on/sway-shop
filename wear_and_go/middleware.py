from django.utils import translation

class QueryLangMiddleware:
    """
    Активирует язык из ?lang=ru/uz или заголовка Accept-Language.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        lang = request.GET.get('lang')

        if not lang:
            header = request.META.get('HTTP_ACCEPT_LANGUAGE', '')
            lang = header.split(',')[0] if header else None

        if lang not in ('ru', 'uz'):
            lang = 'ru'

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response = self.get_response(request)
        translation.deactivate()
        return response
