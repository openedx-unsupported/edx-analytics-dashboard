from django.http import HttpResponse


def status(request):
    return HttpResponse('{"alive": true}', content_type='application/json')
