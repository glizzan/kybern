from django.conf import settings


def load_js_with_webpack(request):
    return {'LOAD_JS_WITH_WEBPACK': settings.LOAD_JS_WITH_WEBPACK}
