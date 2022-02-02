from cgitb import lookup
from django.urls import path, include
from rest_framework.routers import SimpleRouter, DefaultRouter
from rest_framework_nested import routers
from . import views

 # USED WITH THE VIEWSET
router= DefaultRouter() # it will give apiroot at /store
# router= SimpleRouter() # SIMPLE ROUTER DOES NOT GIVE DEFAULT ROOTAPI URL
router.register('productviewset', views.ProductViewSet)
router.register('collectionviewset', views.CollectionViewSet)
# products_router=routers.NestedDefaultRouter(router, 'products', lookup='product')
# products_router.register('reviews',views.ReviewGeneric, basename='product-reviews')

# if we do not have any url patterns then do like below
# urlpatterns=router.urls

# URLConf
urlpatterns = [
    path('', include(router.urls)),
    # path('', include(products_router.urls)),DjangoFilterCollection
    path('djangofiltercollection/', views.DjangoFilterCollection.as_view()),
    path('products/collections/<collection_id>', views.FilterCollection.as_view()),
    path('moveproducttocollection/products/<int:pk>/collections/<int:collection_id>/', views.MoveProductToCollectionView.as_view()),
    path('products/<int:product_id>/reviews/',views.ReviewGeneric.as_view()),
    path('reviews/<int:pk>/',views.ReviewDetailGeneric.as_view()),
    path('mixproductslistsimple/',views.MixProductListSimple.as_view()),
    path('mixproductslistsimple/<slug>/', views.MixProductDetail.as_view()),
    path('mixproducts/',views.MixProductList.as_view()),
    path('classproducts/',views.ProductList.as_view()),
    path('classproducts/<slug>/', views.ProductDetail.as_view()),
    path('products/', views.product_list),
    path('products/<int:id>/', views.product_detail),
    path('products2/<int:id>/', views.product_detail_alternate),
    path('mixclasscollections/', views.MixCollectionList.as_view()),
    path('mixclasscollections/<int:pk>/', views.MixCollectionDetails.as_view()),
    path('classcollections/', views.CollectionList.as_view()),
    path('classcollections/<int:pk>/', views.CollectionDetails.as_view()),
    path('collections/', views.collection_list),
    path('collections/<int:pk>/', views.collection_detail,name='collection-detail'), 
]
#name='collection-detail' is related to line 66 in serializer.py
