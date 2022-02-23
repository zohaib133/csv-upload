import datetime
import os
from django.conf import settings
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from client.response_handler import FailureResponse
from client.models import LogEntryForException


class RequestHandler:
    def __init__(self, request):
        self.request = request
        self.user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        self.requested_url = self.request.META.get('HTTP_REFERER', '')
        self.ip_address = self.get_client_ip_address_from_request()
        self.get_client_ip_address_from_request()

    def get_client_ip_address_from_request(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')
        if not ip_address:
            ip_address = ''
        return ip_address

    def _exception_log_entry(self, exception):
        LogEntryForException.objects.create(exception=exception, url=self.requested_url,
                                            user_agent=self.user_agent,
                                            ip_address=self.ip_address,
                                            created_at=int(datetime.datetime.utcnow().timestamp()))
        return


def respond_with_status_code(value):
    return Response(value, status=value['meta']['status'])


class DecoratorHandler:

    @staticmethod
    def return_http_response(response):
        return response

    def authenticated_rest_call(self, allowed_method_list):
        def decorator(view):
            @api_view(allowed_method_list)
            @permission_classes([IsAuthenticated])
            def wrapper(request, *args, **kwargs):
                request_handler = RequestHandler(request)
                try:
                    time_zone_value = request.META['HTTP_TIME_ZONE_OFF_SET'] \
                        if 'HTTP_TIME_ZONE_OFF_SET' in request.META else 0
                    request.user_agent = request_handler.user_agent
                    request.user_path = request_handler.requested_url
                    request.ip_address = request_handler.ip_address
                    request.time_zone_value = time_zone_value
                    response = view(request, *args, **kwargs)
                except Exception as e:
                    print(e)
                    request_handler._exception_log_entry(e)
                    response = self.return_http_response(
                        FailureResponse(str(e)).return_response_object())
                return response

            return wrapper

        return decorator

    def public_rest_call(self, allowed_method_list):
        def decorator(view):
            @api_view(allowed_method_list)
            @permission_classes([AllowAny])
            def wrapper(request, *args, **kwargs):
                request_handler = RequestHandler(request)
                try:
                    time_zone_value = request.META['HTTP_TIME_ZONE_OFF_SET'] \
                        if 'HTTP_TIME_ZONE_OFF_SET' in request.META else 0
                    request.user_agent = request_handler.user_agent
                    request.user_path = request_handler.requested_url
                    request.ip_address = request_handler.ip_address
                    request.time_zone_value = time_zone_value
                    response = view(request, *args, **kwargs)
                except Exception as e:
                    print(e)
                    request_handler._exception_log_entry(e)
                    response = self.return_http_response(
                        FailureResponse(str(e)).return_response_object())
                return response

            return wrapper

        return decorator


class IsAuthenticatedUser(permissions.BasePermission):
    message = 'None of permissions requirements fulfilled.'

    def has_permission(self, request, view):
        if request.user:
            return True
        else:
            return False

