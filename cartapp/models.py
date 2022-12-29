from django.db import models

class ProductModel(models.Model):
    pname =  models.CharField(max_length=100, default='')
    pprice = models.IntegerField(default=0)
    pimages = models.CharField(max_length=100, default='')
    pdescription = models.TextField(blank=True, default='')
    def __str__(self):
        return self.pname
        
class OrdersModel(models.Model):
    subtotal = models.IntegerField(default=0)
    shipping = models.IntegerField(default=0)
    grandtotal = models.IntegerField(default=0)
    customname =  models.CharField(max_length=100, default='')
    customemail =  models.CharField(max_length=100, default='')
    customaddress =  models.CharField(max_length=100, default='')
    customphone =  models.CharField(max_length=100, default='')
    paytype =  models.CharField(max_length=50, default='')
    def __str__(self):
        return self.customname
     
class DetailModel(models.Model):
    dorder = models.ForeignKey('OrdersModel', on_delete=models.CASCADE)
    pname = models.CharField(max_length=100, default='')
    unitprice = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    dtotal = models.IntegerField(default=0)
    def __str__(self):
        return self.pname

#留言板
class BoardUnit(models.Model):
    bname = models.CharField(max_length=20, null=False)
    bgender = models.CharField(max_length=2, default='m', null=False)
    bsubject = models.CharField(max_length=100, null=False)
    btime = models.DateTimeField(auto_now=True)
    bmail = models.EmailField(max_length=100, blank=True, default='')
    bweb = models.CharField(max_length=200, blank=True, default='')
    bcontent = models.TextField(null=False)
    bresponse = models.TextField(blank=True, default='')
    def __str__(self):
        return self.bsubject

#網路相簿

class AlbumModel(models.Model):
    adate = models.DateTimeField(auto_now=True)
    alocation = models.CharField(max_length=200, blank=True, default='')
    atitle = models.CharField(max_length=100, null=False)
    adesc = models.TextField(blank=True, default='')
    def __str__(self):
        return self.atitle

class PhotoModel(models.Model):
    palbum = models.ForeignKey('AlbumModel', on_delete=models.CASCADE)
    psubject = models.CharField(max_length=100, null=False)
    pdate = models.DateTimeField(auto_now=True)
    purl = models.CharField(max_length=100, null=False)
    phit = models.IntegerField(default=0)
    def __str__(self):
        return self.psubject

#Google Map

class maplist(models.Model):
    mapName = models.CharField(max_length=60, null=False)
    mapDesc = models.TextField(null=False)
    mapLat = models.CharField(max_length=20, null=False)
    mapLng =  models.CharField(max_length=20, null=False)
    mapTel = models.CharField(max_length=20, null=False)
    mapAddr = models.CharField(max_length=60, null=False)
    def __str__(self):
        return self.mapName

#News

class NewsUnit(models.Model):
    catego = models.CharField(max_length=10, null=False)
    nickname = models.CharField(max_length=20, null=False)
    ntitle = models.CharField(max_length=50, null=False)
    message = models.TextField(null=False)
    pubtime = models.DateTimeField(auto_now=True)
    enabled = models.BooleanField(default=False)
    press = models.IntegerField(default=0)
    def __str__(self):
        return self.ntitle
