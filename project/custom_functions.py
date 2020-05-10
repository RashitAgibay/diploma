from django.http import JsonResponse


def api2_response(self_object) -> JsonResponse:
    """ Json Response for API Version 2
        needs to object self values
        status_code = status.HTTP_200_OK

    """

    return JsonResponse(
        {
            'response': {
                'code': self_object.status_code,
                'detail': self_object.detail,
                'data': self_object.data
            }
        }, safe=self_object.safe
    )
