from rest_framework import serializers

from client.models import *


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = "__all__"


class SaleBulkSerializer(serializers.ListSerializer):

    def create(self, validated_data):
        """
            override create method for bulk insertion to assign
            value to field creation_method = 'Single'
        """
        sales_ = []
        # Iterate over records to update creation_method value
        for record in validated_data:
            sales_.append(Sale(**record))
        return Sale.objects.bulk_create(sales_)


class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ('id', 'product', 'revenue', 'sales_number', 'date', 'user_id')
        read_only_fields = ['id', 'created_at', 'updated_at', 'removed_at', 'removed_by', 'created_by',
                            'updated_by', 'is_removed']
        list_serializer_class = SaleBulkSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'gender', 'email')
        read_only_fields = ['id', 'created_at', 'updated_at', 'removed_at', 'removed_by', 'created_by',
                            'updated_by', 'is_removed']
