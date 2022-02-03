from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.generics import UpdateAPIView, CreateAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.core.exceptions import ValidationError
from store.pagination import DefaultPagination
from .filters import ProductFilter
from .models import Collection, OrderItem, Product, Review
from django.db.models import Count
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer

# Create your views here.

#---------------START OF USING VIEWSETS TO AVOID DUPLICACY IN GENERIC VIEWS--------------------#
#---------------(PREFERABLY NOT GOING TO USE DUE TO CUSTOMIZATION ISSUES)......................#

class ProductViewSet(ModelViewSet):
    
    #so all common expressions put in a place like below
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_serializer_context(self):
        return {'request': self.request}
    
    def destroy(self, request, *args, **kwargs):
        if  OrderItem.objects.filter(product_id=kwargs['pk']).count >0:
            return Response("can not be deleted")
        return super().destroy(request, *args, **kwargs)
    
class CollectionViewSet(ModelViewSet):
    
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class= CollectionSerializer
    
    def destroy(self, request, *args, **kwargs):
        if  Product.objects.filter(collection_id=kwargs['pk']).count >0:
            return Response("can not be deleted")
        return super().destroy(request, *args, **kwargs)
    
    
#---------------END OF USING VIEWSETS TO AVOID DUPLICACY IN GENERIC VIEWS--------------------#


#-----------------------START OF REQUEST MADE BY GENERIC VIEWS--------------------------------#
#--------------(PREFFERED TO USE IN THE PRODUCT DUE TO CUSTOMIZATIONS)------------------------#

class MoveProductToCollectionView(UpdateAPIView):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_field = 'pk'
    
    def perform_update(self, serializer):
        related_product = Product.objects.get(id = self.kwargs['pk'])
        related_collection = Collection.objects.get(id = self.kwargs['collection_id'])
        if related_product.collection.id == related_collection.id :
           raise ValidationError ('Source and Destination can not be Same:')
        
        elif (Product.objects.filter(collection__id = self.kwargs['collection_id']).count() > 0):
            raise ValidationError ("Product can not be Moved as collection has only one product")
        else :
            serializer.save(collection = related_collection)

#------------------------------------(START OF FILTERATION)------------------------------------------#


class FilterCollection(ListCreateAPIView):
    
    serializer_class = ProductSerializer
    # lookup_field = 'collection_id'   
    
    def get_queryset(self, *args, **kwargs):
        # related_collection = get_object_or_404(Collection,id = self.kwargs['collection_id'])
        # return related_collection.products.all()
        return Product.objects.filter(collection_id = self.kwargs['collection_id'])
    

class FilterCollectionRetr(RetrieveUpdateDestroyAPIView):
    
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    lookup_field = 'pk'
      
   
class DjangoFilterProduct(ListCreateAPIView):
    
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    # filterset_fields = ['collection_id'] #in case if we are defining any class
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title' , 'description' , 'collection__title']
    ordering_fields = ['unit_price' , 'last_update']
    

class ReviewGeneric(ListCreateAPIView):
    
    serializer_class = ReviewSerializer
    def get_queryset(self, *args, **kwargs):
        return Review.objects.filter(product__id = self.kwargs['product_id'])

    
    
class ReviewDetailGeneric(RetrieveUpdateDestroyAPIView):
    
    serializer_class = ReviewSerializer
    def get_queryset(self):
        return Review.objects.all()
   
    lookup_field = 'pk'
    
#------------------------------------END OF FILTERATION---------------------------------------#    



class MixProductListSimple(ListCreateAPIView): #combines get post methods
    # USING BELOW ARGUMENTS AS WE DO NOT HAVE ANY SPECIAL LOGIC 
    # AND JUST WANT TO RETURN A simple expression
    queryset=Product.objects.select_related('collection').all()
    serializer_class=ProductSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    # filterset_fields = ['collection_id'] #in case if we are defining any class
    filterset_class = ProductFilter
    search_fields = ['title' , 'description' ]
    ordering_fields = ['unit_price' , 'last_update']
    
    def get_serializer_context(self):
        return {'request': self.request}

# Usinf gneneric views we can implement Get/Put/Delete like Below:
class MixProductDetail(RetrieveUpdateDestroyAPIView):
    
    queryset= Product.objects.select_related('collection').all()
    serializer_class = ProductSerializer
    lookup_field = 'slug' #Always try to avoid that and use fix conventions.'slug' was id previously
    # for this just change id to pk in the urls
    
    def delete(self, request, slug): #slug=id previously
        product= get_object_or_404(Product,slug=slug) #pk=id
        if product.orderitems.count()>0:
            return Response("can not be deleted")
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MixCollectionList(ListCreateAPIView):
    
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class= CollectionSerializer

class MixCollectionDetails(RetrieveUpdateDestroyAPIView):
    
    queryset = Collection.objects.annotate(products_count=Count('products')).all()
    serializer_class = CollectionSerializer
    
    def delete(self, request, pk):#As we have some conditions in this.
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

#-----------------END OF REQUEST MADE BY GENERIC VIEWS (BEST SOLUTION TO FOLLOW)---------------#

#----------------------ADDITIONAL CONDITIONS SERVED IN GENERIC VIEWS--------------------------#

class MixProductList(ListCreateAPIView):

    #  Use the below methods if we have some different logics or return some
    # extra informations in the queryset.
    def get_queryset(self):
        return Product.objects.select_related('collection').all()

    def get_serializer_class(self):
        return ProductSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}



#------------------------#START OF CLASS BASED api VIEWS--------------------------------------#

      # (use for much cleaner code and to bypass the if else conditions)
class ProductList(APIView):
    def get(self,request):
        queryset=Product.objects.select_related('collection').all()
        serializer=ProductSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,status=status.HTTP_201_CREATED)

class ProductDetail(APIView):
    def get(self, request, slug):
        product = get_object_or_404(Product, slug=slug)
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    def put(self, request, slug):
        product= get_object_or_404(Product, slug=slug)
        serializer = ProductSerializer(product, data= request.data)
        serializer.is_valid(raise_exception= True)
        serializer.save()
        return Response({'Successfully Updated'})
    
    def delete(self, request, slug):
        product= get_object_or_404(Product, slug=slug)
        if product.orderitems.count()>0:
            return Response("can not be deleted")
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionList(APIView):
    def get(self,request):
        queryset = Collection.objects.annotate(products_count=Count('products')).all()
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class CollectionDetails(APIView):
    def get(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        serailizer= CollectionSerializer(collection)
        return Response(serailizer.data)
    
    def put (self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'Successfully Updated'})
    
    def delete(self, request, pk):
        collection=get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)        

#-------------------------END OF CLASS BASED API VIEWS----------------------------------------#


#-------------------------START OF FUNCTION BASED API VIEWS-----------------------------------#

@api_view(['GET','POST']) 
#arguments should be passed to deserialize the data. default is 'get'.
def product_list(request):
    
    if request.method == 'GET' :
        queryset = Product.objects.select_related('collection').all()
        #select _related is here to return the collection's fields.
        #if select_related not given an infinite loop generates as we 
        #overrided the str method in models.
        
        serializer = ProductSerializer(queryset, many=True, context={'request': request})
        # As it return full data so many will be true
        # context value is given to execute the hyperlinkfield used in serializers.py
        return Response(serializer.data)
    
    elif request.method == 'POST': #deserialization happens
        serializer = ProductSerializer(data=request.data)

        # if serializer.is_valid():
        #     serializer.validated_data
        #     return Response ('ok')
        # else:
        #     return Response (serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    # Alternate of above code
        serializer.is_valid(raise_exception=True)
        serializer.save() #to save in database so we do not need the line 35
        # print(serializer.validated_data)
        return Response (serializer.data, status=status.HTTP_201_CREATED)


@api_view()
def product_detail_alternate(request, id):
    try:
            product = Product.objects.get(pk=id)
            serializer = ProductSerializer(product) #converts python dictionary to json
            return Response(serializer.data)
    except  Product.DoesNotExist: #if the product is not available
            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id): 
    #Bypassing of try and except
    product = get_object_or_404(Product, pk=id) #2 parameters required first is model name other is look up rule

    if request.method =='GET':
        serializer = ProductSerializer(product) #converts python dictionary to json
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer= ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        # if product.orderitem_set.count()>0: # if we not use any related name
        if product.orderitems.count()>0: #here we are using related name from models.py line 85
            return Response({'error: not deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET','POST']) 
def collection_list(request):
    
    if request.method == 'GET' :
         queryset = Collection.objects.annotate(products_count=Count('products')).all()
         serializer = CollectionSerializer(queryset, many=True)
         return Response(serializer.data)

    elif request.method == 'POST':
         serializer = CollectionSerializer(data=request.data)
         serializer.is_valid(raise_exception=True)
         serializer.save()
         return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(
        Collection.objects.annotate(
            products_count=Count('products')), pk=pk)
    
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted because it includes one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)


#-------------------------END OF FUNCTION BASED API VIEWS-----------------------------------#
