from django.http import HttpResponse


# pylint: disable=unused-argument
def status(request):
    return HttpResponse('{"alive": true}', content_type='application/json')
