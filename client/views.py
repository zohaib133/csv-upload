import datetime

from django.contrib.auth import authenticate
from django.db.models import Avg, Max, Sum, Count
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from client.request_handler import DecoratorHandler
from client.serializers import CountrySerializer, CitySerializer, UserSerializer, SaleSerializer
from client.models import Country, City, User, Sale
from client.pagination import PaginationClass
from client.response_handler import SuccessResponse, FailureResponse
from client.constants import SUCCESS_RESPONSE_CODE, BAD_REQUEST_CODE
from rest_framework import mixins, status, viewsets
import csv
DRequests = DecoratorHandler()


@DRequests.authenticated_rest_call(allowed_method_list=['GET'])
def get_countries(request):
    countries = Country.objects.all()
    data = PaginationClass(countries, CountrySerializer, request)
    data = data.paginate()
    return SuccessResponse(data=data,
                           status_code=SUCCESS_RESPONSE_CODE).return_response_object()


@DRequests.authenticated_rest_call(allowed_method_list=['GET'])
def get_cities(request):
    cities = City.objects.filter(country_id=request.GET.get('country_id'))
    data = PaginationClass(cities, CitySerializer, request)
    data = data.paginate()
    return SuccessResponse(data=data,
                           status_code=SUCCESS_RESPONSE_CODE).return_response_object()


@DRequests.authenticated_rest_call(allowed_method_list=['PATCH'])
def patch_user_profile(request):
    serializer = UserSerializer(request.user, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return SuccessResponse(data={},
                               message="User updated",
                               status_code=SUCCESS_RESPONSE_CODE).return_response_object()
    return FailureResponse(errors=serializer.errors,
                           message="fail to update user",
                           status_code=BAD_REQUEST_CODE).return_response_object()


@DRequests.authenticated_rest_call(allowed_method_list=['GET'])
def get_profile(request):
    serializer = UserSerializer(request.user)
    return SuccessResponse(data=serializer.data,
                           message="User Detail Found Successfully",
                           status_code=SUCCESS_RESPONSE_CODE).return_response_object()


@DRequests.authenticated_rest_call(allowed_method_list=['GET'])
def sale_statistics(request):
    sale = Sale.objects.filter(user_id=request.user).values_list('sales_number', 'revenue', 'product')
    total_revenue = sum([x[1] for x in sale.iterator()])
    avg_sale = total_revenue / len(sale)

    sale_ = Sale.objects.aggregate(Sum('revenue'), Count('id'))
    total_sale_ = sale_['revenue__sum'] / sale_['id__count']

    max_revenue = Sale.objects.filter(user_id=request.user).order_by('-revenue').first()
    max_revenue_, max_revenue_sale_id, product_based_rev, product_based_revv, product_high_sale, product_high_salee = '', '', '', '', '', ''
    if max_revenue:
        max_revenue_ = max_revenue.revenue
        max_revenue_sale_id = max_revenue.id

    result = Sale.objects.filter(user_id=request.user).values('product').annotate(dcount=Sum('revenue')).order_by('-dcount').first()
    if result:
        product_based_rev = result['product']
        product_based_revv = result['dcount']

    result = Sale.objects.filter(user_id=request.user).values('product').annotate(dcount=Count('sales_number')).order_by('-sales_number').first()
    if result:
        product_high_sale = result['product']
        product_high_salee = result['dcount']

    data = {
        "average_sale_for_current_user": avg_sale,
        "average_sale_all_user": total_sale_,
        "highest_revenue_sale_for_current_user": {
            "sale_id": max_revenue_sale_id,
            "revenue": max_revenue_
        },
        "product_revenue_for_current_user": {
            "product_name": product_based_rev,
            "price": product_based_revv
        },
        "product_highest_sales_number_for_current_user": {
            "product_name": product_high_sale,
            "price": product_high_salee
        },
    }
    return SuccessResponse(data=data,
                           message="User Stats Found Successfully",
                           status_code=SUCCESS_RESPONSE_CODE).return_response_object()


@DRequests.authenticated_rest_call(allowed_method_list=['POST'])
def upload_sales_file(request):
    file = request.FILES['file']
    file_data = file.read().decode("utf-8")
    lines = file_data.split("\n")

    line_count_ = 0
    records = []
    for row in lines:
        line_count_ = line_count_ + 1
        if line_count_ == 1:
            pass
        else:
            row = row.split(",")
            if len(row) < 4:
                continue

            dict_ = {
                'date': row[0],
                'product': row[1],
                'sales_number': row[2],
                'revenue': float(row[3].strip()),
                'user_id': request.user.id
            }
            records.append(dict_)

    serializer = SaleSerializer(data=records, many=True)
    if serializer.is_valid():
        serializer.save()
        return SuccessResponse(data={},
                               message="data updated",
                               status_code=SUCCESS_RESPONSE_CODE).return_response_object()
    return FailureResponse(errors=serializer.errors,
                           message="fail to add user",
                           status_code=BAD_REQUEST_CODE).return_response_object()


class UserViewSet(mixins.UpdateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)


class SaleViewSet(mixins.UpdateModelMixin,
                  mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = (IsAuthenticated,)


@DRequests.public_rest_call(allowed_method_list=['POST'])
def login(request):
    import json
    data = json.loads(request.body.decode('utf-8'))
    username = data['email'].lower().strip()
    password = data['password'] if 'password' in data else None

    user = authenticate(username=username, password=password)
    if not user or not user.is_active:
        return FailureResponse(message='Invalid username/password',
                               status_code=BAD_REQUEST_CODE).return_response_object()

    refresh_token = RefreshToken.for_user(user)
    return SuccessResponse(data={'token': str(refresh_token.access_token), 'user_id': user.id},
                           message='Login Successfully!').return_response_object()

