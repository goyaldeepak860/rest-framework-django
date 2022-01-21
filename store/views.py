from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, response
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
# Create your views here.


@api_view() #outer function
def product_list(request):
    queryset = Product.objects.select_related('collection').all()
    #select _related is here to return the collection name.
    #if select_related not given an infinite loop generates as we 
    #overrided the str method in models.
    
    serializer = ProductSerializer(queryset, many=True, context={'request': request})
    # As it return full data so many will be true
    # context value is given to execute the hyperlinkfield used in serializers.py
    return Response(serializer.data)

@api_view()
def product_detail(request, id):
    try:
            product = Product.objects.get(pk=id)
            serializer = ProductSerializer(product) #converts python dictionary to json
            return Response(serializer.data)
    except  Product.DoesNotExist: #if the product is not available
            return Response(status=status.HTTP_404_NOT_FOUND)

@api_view()
def product_detail_alternate(request, id): #Bypassing of try and except
    product = get_object_or_404(Product, pk=id) #2 parameters required first is model name other is look up rule
    serializer = ProductSerializer(product) #converts python dictionary to json
    return Response(serializer.data)

@api_view()
def collection_detail(request, pk):
    return Response('ok')
    
   