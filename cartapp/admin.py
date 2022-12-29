from django.contrib import admin
from cartapp import models
from cartapp.models import maplist

admin.site.register(models.ProductModel)
admin.site.register(models.OrdersModel)
admin.site.register(models.DetailModel)

admin.site.register(models.BoardUnit) #留言板

admin.site.register(models.AlbumModel) #網路相簿
admin.site.register(models.PhotoModel)

class maplistAdmin(admin.ModelAdmin): #Google Map
    list_display=('mapName','mapDesc','mapLat','mapLng','mapTel','mapAddr')

admin.site.register(maplist,maplistAdmin)

admin.site.register(models.NewsUnit) #公告