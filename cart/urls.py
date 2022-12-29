"""cart URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from cartapp import views
from django.conf.urls import include
from django.conf import settings#網路相簿
from django.conf.urls.static import static#網路相簿

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('index/', views.index),
    path('cart_index/', views.cart_index),#購物車
    path('detail/<int:productid>/', views.detail),
    path('addtocart/<str:ctype>/', views.addtocart),
    path('addtocart/<str:ctype>/<int:productid>/', views.addtocart),
    path('cart/', views.cart),
    path('cartorder/', views.cartorder),
    path('cartok/', views.cartok),
    path('cartordercheck/', views.cartordercheck),
    path('board_index/', views.board_index),#留言板
    path('board_post/', views.board_post),
    path('captcha/', include('captcha.urls')),#驗證碼
    path('board_login/', views.board_login),
    path('board_logout/', views.board_logout),
    path('board_adminmain/', views.board_adminmain),
    path('board_adminmain/<str:pageindex>/', views.board_adminmain),
    path('board_delete/<int:boardid>/', views.board_delete),
    path('board_delete/<int:boardid>/<str:deletetype>/', views.board_delete),
    path('album_index/', views.album_index),#網路相簿
    path('album_show/<int:albumid>/', views.album_show),
    path('album_photo/<int:photoid>/<int:albumid>/', views.album_photo),
    path('album_login/', views.album_login),
    path('album_logout/', views.album_logout),
    path('album_adminmain/', views.album_adminmain),
    path('album_adminmain/<int:albumid>/', views.album_adminmain),
    path('album_adminadd/', views.album_adminadd),
    path('album_adminfix/<int:albumid>/', views.album_adminfix),
    path('album_adminfix/<int:albumid>/<int:photoid>/', views.album_adminfix),
    path('album_adminfix/<int:albumid>/<int:photoid>/<str:deletetype>/', views.album_adminfix),
    path('map_index/',views.map_index),#Google Map
    path('map_login/',views.map_login),
	path('map_logout/',views.map_logout),
	path('map_adminmain/',views.map_adminmain),
	path('map_adminadd/',views.map_adminadd),
	path('map_adminedit/',views.map_adminedit),
    path('map_adminedit/<int:editid>/',views.map_adminedit),
    path('map_admindelete/',views.map_admindelete),
	path('news_index/', views.news_index),#News
	path('news_index/<str:pageindex>/', views.news_index),
	path('news_detail/<int:detailid>/', views.news_detail),
	path('news_login/', views.news_login),
	path('news_logout/', views.news_logout),
	path('news_adminmain/', views.news_adminmain),
	path('news_adminmain/<str:pageindex>/', views.news_adminmain),
 	path('news_add/', views.news_add),
	path('news_edit/<int:newsid>/', views.news_edit),
	path('news_edit/<int:newsid>/<str:edittype>/', views.news_edit),
	path('news_delete/<int:newsid>/', views.news_delete),
	path('news_delete/<int:newsid>/<str:deletetype>/', views.news_delete),
    path('introduction/', views.introduction),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #網路相簿