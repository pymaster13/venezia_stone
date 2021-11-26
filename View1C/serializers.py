from rest_framework import serializers

from .models import *

class MaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materials
        fields = ['ps', 'mt', 'ph', 'photo_material', 'sku', 'kw', 'url']

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['img',]

class InvGroupsSerializer(serializers.ModelSerializer):
    file = serializers.CharField(source='photo_groups')
    num = serializers.CharField(source='nam')

    class Meta:
        model = InvGroups
        fields = ['ps', 'id_color_sort', 'gr', 'co', 'cl', 'num', 'sku', \
        'prRUB', 'prUSD', 'prEUR', 'kw', 'typeFoto', 'file', 'nw', 'onSale', \
        'pz', 'url']

class InvItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvItems
        fields = ['ps', 'id_color_sort', 'name', 'izd', 'pro', 'thn', 'obr', \
        'kat', 'qua', 'cp', 'cs', 'kw', 'prRUB', 'prUSD', 'prEUR', 'sku', \
        'typeFoto', 'photo_item', 'nw', 'onSale', 'pz', 'url']

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['pk', 'ps', 'bl', 'color_range', 'photobl', 'photobltp', 'bty', \
        'le', 'he', 'sco', 'sklad', 'os', 'cntRUB', 'cntUSD', 'cntEUR', 'nw', \
        'onSale', 'pz', 'kolvo', 'obos', 'ossht', 'komment', 'video', 'country',\
         'typeFoto', 'photo_product', 'url', 'itms_name', 'itms_izd','kw']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['pk', 'ps', 'bl', 'color_range', 'photobl', 'photobltp', 'bty', \
        'le', 'he', 'sco', 'sklad', 'os', 'cntRUB', 'cntUSD', 'cntEUR', 'nw', \
        'onSale', 'pz', 'kolvo', 'obos', 'ossht', 'komment', 'video', 'country',\
         'typeFoto', 'photo_product', 'url', 'itms_name', 'itms_izd', 'kw']

class UserAndProduct(serializers.Serializer):
    token = serializers.CharField(required = False, label = 'token')
    id_product = serializers.CharField()
