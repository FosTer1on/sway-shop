from django.utils import translation
import time
import logging


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


logger = logging.getLogger("requests")


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        response = self.get_response(request)

        request_id = request.headers.get("X-Request-ID", "-")

        duration_ms = round((time.perf_counter() - start_time) * 1000)

        user_id = None
        if hasattr(request, "user") and request.user.is_authenticated:
            user_id = request.user.id

        ip = self.get_client_ip(request)

        level = logging.INFO
        if response.status_code >= 500:
            level = logging.ERROR
        elif response.status_code >= 400:
            level = logging.WARNING

        logger.log(
            level,
            "%s %s %s %sms user=%s ip=%s request_id=%s",
            request.method,
            request.get_full_path(),
            response.status_code,
            duration_ms,
            user_id,
            ip,
            request_id,
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR")
