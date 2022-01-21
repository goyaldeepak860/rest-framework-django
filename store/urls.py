from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('products/', views.product_list),
    path('collections/', views.collection_list),
    path('products/<int:id>/', views.product_detail),
    path('products2/<int:id>/', views.product_detail_alternate),
     path('collections/<int:pk>/', views.collection_detail,name='collection-detail'),
]
