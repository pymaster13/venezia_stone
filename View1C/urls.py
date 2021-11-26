"""VeneziaStone URL Configuration"""

from django.urls import path
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from .views import *

urlpatterns = [
    path('Bookmatch/', Bookmatch.as_view() , name="Bookmatch"),
    path('Filter/', Filter.as_view() , name="Filter"),
    path('Product/', Product.as_view() , name="Product"),

    path('showSelectedFavourite/', showSelectedFavourite.as_view() , name="showSelectedFavourite"),
    path('showSelectedViewed/', showSelectedViewed.as_view() , name="showSelectedViewed"),

    path('showFavourite/', showFavourite.as_view() , name="showFavourite"),
    path('showViewed/', showViewed.as_view() , name="showViewed"),

    path('addFavourite/', addFavourite.as_view() , name="addFavourite"),
    path('addViewed/', addViewed.as_view() , name="addViewed"),

    path('deleteFavourite/', deleteFavourite.as_view() , name="deleteFavourite"),
    path('deleteViewed/', deleteViewed.as_view() , name="deleteViewed"),

    path('getMaterials/', getMaterials.as_view() , name="getMaterials"),
    path('getFilters/', getFilters.as_view() , name="getFilters"),
    path('getUpperFilters/', getUpperFilters.as_view() , name="getUpperFilters"),

    path('get_photo_for_pdf/', get_Photo_for_PDF.as_view() , name="get_Photo_for_PDF"),
    path('get_photo_bytes/', getPhotoBytes.as_view() , name="getPhotoBytes"),

    path('upperFilter/<str:izd>/', upperFilter.as_view() , name="upperFilter"),
    path('Search/<str:nm>/', Search.as_view() , name="Search"),

    path('sale/<str:material>/', getGroupsSale.as_view() , name="getGroupsSale"),
    path('sale/<str:material>/<str:group>/<str:item>/', getProductsSale.as_view() , name="getProductsSale"),
    path('sale/<str:material>/<str:group>/', getGroupsElementSale.as_view() , name="getGroupsElementSale"),
    path('sale/<str:material>/<str:group>/<str:item>/<str:product>/', getProductSale.as_view() , name="getProductSale"),
    #
    path('new/<str:material>/', getGroupsNew.as_view() , name="getGroupsNew"),
    path('new/<str:material>/<str:group>/', getGroupsElementNew.as_view() , name="getGroupsElementNew"),
    path('new/<str:material>/<str:group>/<str:item>/', getProductsNew.as_view() , name="getProductsNew"),
    path('new/<str:material>/<str:group>/<str:item>/<str:product>/', getProductNew.as_view() , name="getProductNew"),

    path('<str:material>/', getGroups.as_view() , name="getGroups"),
    path('<str:material>/<str:group>/', getGroupsElement.as_view() , name="getGroupsElement"),
    path('<str:material>/<str:group>/<str:item>/', getProducts.as_view() , name="getProducts"),
    path('<str:material>/<str:group>/<str:item>/<str:product>/', getProduct.as_view() , name="getProduct"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()
