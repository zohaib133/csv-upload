from rest_framework.response import Response

from client.constants import *


class SuccessResponse:
    def __init__(self, data=None, message="",
                 status_code=SUCCESS_RESPONSE_CODE, errors=None):
        if errors is None:
            errors = []
        if data is None:
            data = {}
        self.data = data
        self.message = message
        self.status_code = status_code
        self.errors = errors

    def response_object(self):
        return {
            'data': self.data,
            'meta': {
                "status": self.status_code,
                "message": self.message,
                "errors": self.errors
            }
        }

    def return_response_object(self):
        return respond(self.response_object())


class FailureResponse:
    def __init__(self, message='Something Went Wrong', status_code=INTERNAL_SERVER_ERROR,
                 errors=None):
        if errors is None:
            errors = []
        self.message = message
        self.status_code = status_code
        self.errors = errors

    def response_object(self):
        return {
            'data': {},
            'meta': {
                "status": self.status_code,
                "message": self.message,
                "errors": self.errors
            }
        }

    @staticmethod
    def method_not_allowed():
        dict_ = {
            'data': {},
            'meta': {
                "status": METHOD_NOT_ALLOWED,
                "message": "METHOD_NOT_ALLOWED",
                "errors": []
            }
        }
        return respond(dict_)

    @staticmethod
    def unauthorized_object():
        dict_ = {
            'data': {},
            'meta': {
                "status": UNAUTHORIZED,
                "message": 'Unauthorized User',
                "errors": []
            }
        }
        return respond(dict_)

    @staticmethod
    def bad_url_object():
        dict_ = {
            'data': {},
            'meta': {
                "status": PAGE_NOT_FOUND,
                "message": 'Page not found',
                "errors": []
            }
        }
        return respond(dict_)

    @staticmethod
    def something_went_wrong():
        dict_ = {
            'data': {},
            'meta': {
                "status": INTERNAL_SERVER_ERROR,
                "message": 'Something went wrong',
                "errors": []
            }
        }
        return respond(dict_)

    def return_response_object(self):
        return respond(self.response_object())


def respond(response_):
    return Response(response_['data'], status=response_['meta']['status'])


def handler404error(request, exception):
    return FailureResponse().bad_url_object()


def handler500error(request, exception=None):
    return FailureResponse().something_went_wrong()
