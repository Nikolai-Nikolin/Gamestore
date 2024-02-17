from django.http import JsonResponse


def ping(request):
    data = {'message': 'Server is up and running'}
    return JsonResponse(data)

