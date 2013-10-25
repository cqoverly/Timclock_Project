from django.http import HttpResponse


def vw_hello(request):
    return HttpResponse('Hello, and thanks for working.')
