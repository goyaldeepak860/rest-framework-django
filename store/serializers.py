from decimal import Decimal
from store.models import Product, Collection, Review
from rest_framework import serializers


# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)
    
# Use of ModelSerializer(used to avoid duplication), 
# that must be preffered appraoach than the above one

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'slug',
            'inventory',
            'unit_price',
            'price_with_tax',
            'collection',
            'price_with_vat' #default it will print the primary key of model
        ] # order of fields always matters
    # fields=' __all__' to get all the fields of a model, this must be avoided
    
    
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    #always stay on conventions so do not use any other field name.
    # first it will look up all field in model if it is not there it will come on declared section.
    # we can use price in the field istead of unit_price
    price_with_vat = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)
    # using Decimal to convert the float value 1.1 into decimal as we have
    # unit_price field in decimal so we can multiply a decimal to a float
    # so we need this object Decimal.
    
    # below line is printing the collection id
    # collection = serializers.PrimaryKeyRelatedField(
    #     queryset= Collection.objects.all()
    # )
    
    # this line will print the title of each collection. torun this comment the above code and vice-versa
    # collection = serializers.StringRelatedField()

    # below code is using collection as aobject
    # print the fields for CollectionSerialzer class
    # collection = CollectionSerializer()
    
    #below will be used to include a end point hyperlink
    # collection = serializers.HyperlinkedRelatedField (
    #     queryset = Collection.objects.all(),
    #     view_name = 'collection-detail'
    # )

#in the case of user registarion we need to ovweride the validation method like this
# def validate(self, data):
#     if data['password'] != data['confirm password']:
#         return serializers.ValidationError('do not match')
#     return data


class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True) #Fetching the records of products
    products_count = serializers.IntegerField(read_only=True)
    class Meta:
        model = Collection
        fields = [
            'id',
            'title',
            'products_count',
            'products'
        ] #Should be in alphabatical order
    


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            'id',
            'date',
            'name',
            'product',
            'description',
            'uuid'
        ]
    uuid = serializers.UUIDField(read_only=True)
