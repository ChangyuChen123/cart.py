from django.shortcuts import render, redirect
from cartapp import models, forms
from smtplib import SMTP, SMTPAuthenticationError, SMTPException
from email.mime.text import MIMEText
from django.contrib.auth import authenticate
from django.contrib import auth
import math
from django.core.files.storage import FileSystemStorage #網路相簿
from django.conf import settings
import os
from datetime import datetime #Google Map
from cartapp.models import maplist
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages #News
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django import template
import math

message = ''
cartlist = []  #購買商品串列
customname = ''  #購買者姓名
customphone = ''  #購買者電話
customaddress = ''  #購買者地址
customemail = ''  #購買者電子郵件

page = 0  #目前頁面,0為第1頁(留言板)
page1 = 1 #公告News

def index(request):

	return render(request, "index.html", locals())




def cart_index(request):
	global cartlist
	if 'cartlist' in request.session:  #若session中存在cartlist就讀出
		cartlist = request.session['cartlist']
	else:  #重新購物
		cartlist = []
	cartnum = len(cartlist)  #購買商品筆數
	productall = models.ProductModel.objects.all()  #取得資料庫所有商品
	return render(request, "cart_index.html", locals())

def detail(request, productid=None):  #商品詳細頁面
	product = models.ProductModel.objects.get(id=productid)  #取得商品
	return render(request, "detail.html", locals())

def cart(request):  #顯示購物車
	global cartlist
	cartlist1 = cartlist  #以區域變數傳給模版
	total = 0
	for unit in cartlist:  #計算商品總金額
		total += int(unit[3])
	grandtotal = total + 100  #加入運費總額
	return render(request, "cart.html", locals())

def addtocart(request, ctype=None, productid=None):
	global cartlist
	if ctype == 'add':  #加入購物車
		product = models.ProductModel.objects.get(id=productid)
		flag = True  #設檢查旗標為True
		for unit in cartlist:  #逐筆檢查商品是否已存在
			if product.pname == unit[0]:  #商品已存在
				unit[2] = str(int(unit[2])+ 1)  #數量加1
				unit[3] = str(int(unit[3]) + product.pprice)  #計算價錢
				flag = False  #設檢查旗標為False
				break
		if flag:  #商品不存在
			temlist = []  #暫時串列
			temlist.append(product.pname)  #將商品資料加入暫時串列
			temlist.append(str(product.pprice))  #商品價格
			temlist.append('1')  #先暫訂數量為1
			temlist.append(str(product.pprice))  #總價
			cartlist.append(temlist)  #將暫時串列加入購物車
		request.session['cartlist'] = cartlist  #購物車寫入session
		return redirect('/cart/')
	elif ctype == 'update':  #更新購物車
		n = 0
		for unit in cartlist:
			unit[2] = request.POST.get('qty' + str(n), '1')  #取得數量
			unit[3] = str(int(unit[1]) * int(unit[2]))  #取得總價
			n += 1
		request.session['cartlist'] = cartlist
		return redirect('/cart/')
	elif ctype == 'empty':  #清空購物車
		cartlist = []  #設購物車為空串列
		request.session['cartlist'] = cartlist
		return redirect('/cart_index/')
	elif ctype == 'remove':  #刪除購物車中商品
		del cartlist[int(productid)]  #從購物車串列中移除商品
		request.session['cartlist'] = cartlist
		return redirect('/cart/')

def cartorder(request):  #按我要結帳鈕
	global cartlist, message, customname, customphone, customaddress, customemail
	cartlist1 = cartlist
	total = 0
	for unit in cartlist:  #計算商品總金額
		total += int(unit[3])
	grandtotal = total + 100
	customname1 = customname  ##以區域變數傳給模版
	customphone1 = customphone
	customaddress1 = customaddress
	customemail1 = customemail
	message1 = message
	return render(request, "cartorder.html", locals())

def cartok(request):  #按確認購買鈕
	global cartlist, message, customname, customphone, customaddress, customemail
	total = 0
	for unit in cartlist:
		total += int(unit[3])
	grandtotal = total + 100
	message = ''
	customname = request.POST.get('CustomerName', '')
	customphone = request.POST.get('CustomerPhone', '')
	customaddress = request.POST.get('CustomerAddress', '')
	customemail = request.POST.get('CustomerEmail', '')
	paytype = request.POST.get('paytype', '')
	customname1 = customname
	if customname=='' or customphone=='' or customaddress=='' or customemail=='':
		message = '姓名、電話、住址及電子郵件皆需輸入'
		return redirect('/cartorder/')
	else:
		unitorder = models.OrdersModel.objects.create(subtotal=total, shipping=100, grandtotal=grandtotal, customname=customname, customphone=customphone, customaddress=customaddress, customemail=customemail, paytype=paytype) #建立訂單
		for unit in cartlist:  #將購買商品寫入資料庫
			total = int(unit[1]) * int(unit[2])
			unitdetail = models.DetailModel.objects.create(dorder=unitorder, pname=unit[0], unitprice=unit[1], quantity=unit[2], dtotal=total)
		orderid = unitorder.id  #取得訂單id
		mailfrom="你的gmail帳號"  #帳號
		mailpw="你的gmail密碼"  #密碼
		mailto=customemail  #收件者
		mailsubject="Herman購物網-訂單通知";  #郵件標題
		mailcontent = "感謝您的光臨，您已經成功的完成訂購程序。\n我們將儘快把您選購的商品郵寄給您！ 再次感謝您支持\n您的訂單編號為：" + str(orderid) + "，您可以使用這個編號回到網站中查詢訂單的詳細內容。\n織夢數位購物網" #郵件內容
		send_simple_message(mailfrom, mailpw, mailto, mailsubject, mailcontent)  #寄信
		cartlist = []
		request.session['cartlist'] = cartlist
		return render(request, "cartok.html", locals())

def cartordercheck(request):  #查詢訂單
	orderid = request.GET.get('orderid', '')  #取得輸入id
	customemail = request.GET.get('customemail', '')  #取得輸email
	if orderid == '' and customemail == '':  #按查詢訂單鈕
		firstsearch = 1
	else:
		order = models.OrdersModel.objects.filter(id=orderid).first()
		if order == None or order.customemail != customemail:  #查不到資料
			notfound = 1
		else:  #找到符合的資料
			details = models.DetailModel.objects.filter(dorder=order)
	return render(request, "cartordercheck.html", locals())

def send_simple_message(mailfrom, mailpw, mailto, mailsubject, mailcontent): #寄信
	global message
	strSmtp = "smtp.gmail.com:587"  #主機
	strAccount = mailfrom  #帳號
	strPassword = mailpw  #密碼
	msg = MIMEText(mailcontent)
	msg["Subject"] = mailsubject  #郵件標題
	mailto1 = mailto  #收件者
	server = SMTP(strSmtp)  #建立SMTP連線
	server.ehlo()  #跟主機溝通
	server.starttls()  #TTLS安全認證
	try:
		server.login(strAccount, strPassword)  #登入
		server.sendmail(strAccount, mailto1, msg.as_string())  #寄信
	except SMTPAuthenticationError:
		message = "無法登入！"
	except:
		message = "郵件發送產生錯誤！"
	server.quit() #關閉連線

#留言板

def board_index(request, pageindex=None):  #首頁
	global page  #重複開啟本網頁時需保留 page1 的值
	pagesize = 3  #每頁顯示的資料筆數
	boardall = models.BoardUnit.objects.all().order_by('-id')  #讀取資料表,依時間遞減排序
	datasize = len(boardall)  #資料筆數
	totpage = math.ceil(datasize / pagesize)  #總頁數
	if pageindex==None:  #無參數
		page = 0
		boardunits = models.BoardUnit.objects.order_by('-id')[:pagesize]
	elif pageindex=='prev':  #上一頁
		start = (page-1)*pagesize  #該頁第1筆資料
		if start >= 0:  #有前頁資料就顯示
			boardunits = models.BoardUnit.objects.order_by('-id')[start:(start+pagesize)]
			page -= 1
	elif pageindex=='next':  #下一頁
		start = (page+1)*pagesize  #該頁第1筆資料
		if start < datasize:  #有下頁資料就顯示
			boardunits = models.BoardUnit.objects.order_by('-id')[start:(start+pagesize)]
			page += 1
	currentpage = page + 1  #將目頁前頁面以區域變數傳回html
	return render(request, "board_index.html", locals())

def board_post(request):  #新增留言
	if request.method == "POST":  #如果是以POST方式才處理
		postform = forms.PostForm(request.POST)  #建立forms物件
		if postform.is_valid():  #通過forms驗證
		  subject = postform.cleaned_data['boardsubject']  #取得輸入資料
		  name =  postform.cleaned_data['boardname']
		  gender =  request.POST.get('boardgender', None)
		  mail = postform.cleaned_data['boardmail']
		  web =  postform.cleaned_data['boardweb']
		  content =  postform.cleaned_data['boardcontent']
		  unit = models.BoardUnit.objects.create(bname=name, bgender=gender, bsubject=subject, bmail=mail, bweb=web, bcontent=content, bresponse='')  #新增資料記錄
		  unit.save()  #寫入資料庫
		  message = '已儲存...'
		  postform = forms.PostForm()
		  return redirect('/board_index/')
		else:
		  message = '驗證碼錯誤！'
	else:
		message = '標題、姓名、內容及驗證碼必須輸入！'
		postform = forms.PostForm()
	return render(request, "board_post.html", locals())

def board_login(request):  #登入
	messages = ''  #初始時清除訊息
	if request.method == 'POST':  #如果是以POST方式才處理
		name = request.POST['username'].strip()  #取得輸入帳號
		password = request.POST['passwd']  #取得輸入密碼
		user1 = authenticate(username=name, password=password)  #驗證
		if user1 is not None:  #驗證通過
			if user1.is_active:  #帳號有效
				auth.login(request, user1)  #登入
				return redirect('/board_adminmain/')  #開啟管理頁面
			else:  #帳號無效
				message = '帳號尚未啟用！'
		else:  #驗證未通過
			message = '登入失敗！'
	return render(request, "board_login.html", locals())

def board_logout(request):  #登出
	auth.logout(request)
	return redirect('/board_index/')

def board_adminmain(request, pageindex=None):  #管理頁面
	global page
	pagesize = 3
	boardall = models.BoardUnit.objects.all().order_by('-id')
	datasize = len(boardall)
	totpage = math.ceil(datasize / pagesize)
	if pageindex==None:
		page =0
		boardunits = models.BoardUnit.objects.order_by('-id')[:pagesize]
	elif pageindex=='prev':
		start = (page-1)*pagesize
		if start >= 0:
			boardunits = models.BoardUnit.objects.order_by('-id')[start:(start+pagesize)]
			page -= 1
	elif pageindex=='next':
		start = (page+1)*pagesize
		if start < datasize:
			boardunits = models.BoardUnit.objects.order_by('-id')[start:(start+pagesize)]
			page += 1
	elif pageindex=='ret':  #按確定修改鈕後返回
		start = page*pagesize
		boardunits = models.BoardUnit.objects.order_by('-id')[start:(start+pagesize)]
	else:  #按確定修改鈕會以pageindex傳入資料id
		unit = models.BoardUnit.objects.get(id=pageindex)  #取得要修改的資料記錄
		unit.bsubject=request.POST.get('boardsubject', '')
		unit.bcontent=request.POST.get('boardcontent', '')
		unit.bresponse=request.POST.get('boardresponse', '')
		unit.save()  #寫入資料庫
		return redirect('/board_adminmain/ret/')  #返回管理頁面,參數為ret
	currentpage = page+1
	return render(request, "board_adminmain.html", locals())

def board_delete(request, boardid=None, deletetype=None):  #刪除資料
	unit = models.BoardUnit.objects.get(id=boardid)  #讀取指定資料
	if deletetype == 'del':  #按確定刪除鈕
		unit.delete()
		return redirect('/board_adminmain/')
	return render(request, "board_delete.html", locals())

#網路相簿

def album_index(request):
	albums = models.AlbumModel.objects.all().order_by('-id')  #讀取所有相簿
	totalalbum = len(albums)  #相簿總數
	photos = []  #每一相簿第1張相片串列
	lengths = []  #每一相簿的相片總數串列
	for album in albums:
		photo = models.PhotoModel.objects.filter(palbum__atitle=album.atitle).order_by('-id')  #讀取相片
		lengths.append(len(photo))  #加入相片總數
		if len(photo) == 0:  #若無相片加入空字串
			photos.append('')
		else:
			photos.append(photo[0].purl)  #加入第1張相片
	return render(request, "album_index.html", locals())

def album_show(request, albumid=None):  #顯示相簿
	album = albumid  #以區域變數傳送給html
	photos = models.PhotoModel.objects.filter(palbum__id=album).order_by('-id')  #讀取所有相片
	monophoto = photos[0]  #第1張相片
	totalphoto = len(photos)  #相片總數
	return render(request, "album_show.html", locals())

def album_photo(request, photoid=None, albumid=None):  #顯示單張相片
	album = albumid  #以區域變數傳送給html
	photo = models.PhotoModel.objects.get(id=photoid)  #取得點選的相片
	photo.phit += 1  #點擊數加1
	photo.save()  #儲存資料
	return render(request, "album_photo.html", locals())

def album_login(request):  #登入
	if request.method == "POST":
		postform = forms.PostForm_album(request.POST)
		if postform.is_valid():  # forms驗證通過
			username = postform.cleaned_data['username']
			pd = postform.cleaned_data['pd']
			user1 = authenticate(username=username, password=pd)  # 管理者驗證
			if user1 is not None:  # 驗證通過
				auth.login(request, user1)  # 登入
				postform = forms.PostForm_album()
				return redirect('/album_adminmain/')
			else:  # 驗證未通過
				message = '登入失敗！'
		else:
			message = '驗證碼錯誤！'
	else:
		message = '帳號、密碼及驗證碼都必須輸入！'
		postform = forms.PostForm_album()
	return render(request, "album_login.html", locals())

def album_logout(request):  #登出
	auth.logout(request)
	return redirect('/album_index/')

def album_adminmain(request, albumid=None):  #管理頁面
	if albumid == None:  #按相簿管理鈕進管理頁面
		albums = models.AlbumModel.objects.all().order_by('-id')
		totalalbum = len(albums)
		photos = []
		lengths = []
		for album in albums:
			photo = models.PhotoModel.objects.filter(palbum__atitle=album.atitle).order_by('-id')
			lengths.append(len(photo))
			if len(photo) == 0:
				photos.append('')
			else:
				photos.append(photo[0].purl)
	else:  #按刪除相簿鈕
		album = models.AlbumModel.objects.get(id=albumid)  #取得相簿
		photo = models.PhotoModel.objects.filter(palbum__atitle=album.atitle).order_by('-id')  #取得所有相片
		for photounit in photo:  #刪除所有相片檔案
			os.remove(os.path.join(settings.MEDIA_ROOT, photounit.purl ))
		album.delete()  #移除相簿
		return redirect('/album_adminmain/')
	return render(request, "album_adminmain.html", locals())

def album_adminadd(request):  #新增相簿
	message = ''
	title = request.POST.get('album_title', '')  #取得輸入資料
	location = request.POST.get('album_location', '')
	desc = request.POST.get('album_desc', '')
	if title=='':  #按新增相簿鈕進入此頁
		message = '相簿名稱一定要填寫...'
	else:  #按確定新增鈕
		unit = models.AlbumModel.objects.create(atitle=title, alocation=location, adesc=desc)
		unit.save()
		return redirect('/album_adminmain/')
	return render(request, "album_adminadd.html", locals())

def album_adminfix(request, albumid=None, photoid=None, deletetype=None):  #相簿維護
    album = models.AlbumModel.objects.get(id=albumid)  #取得指定相簿
    photos = models.PhotoModel.objects.filter(palbum__id=albumid).order_by('-id')
    totalphoto = len(photos)
    if photoid != None:  #不是由管理頁面進入本頁面
        if photoid == 999999:  #按更新及上傳資料鈕
            album.atitle = request.POST.get('album_title', '')  #更新相簿資料
            album.alocation = request.POST.get('album_location', '')
            album.adesc = request.POST.get('album_desc', '')
            album.save()
            files = []  #上傳相片串列
            descs = []  #相片說明串列
            picurl = ["ap_picurl1", "ap_picurl2", "ap_picurl3", "ap_picurl4", "ap_picurl5"]
            subject = ["ap_subject1", "ap_subject2", "ap_subject3", "ap_subject4", "ap_subject5"]
            for count in range(0,5):
                files.append(request.FILES.get(picurl[count], ''))
                descs.append(request.POST.get(subject[count], ''))
            i = 0
            for upfile in files:
                if upfile != '' and descs[i] != '':
                    fs = FileSystemStorage()  #上傳檔案
                    filename = fs.save(upfile.name, upfile)
                    unit = models.PhotoModel.objects.create(palbum=album, psubject=descs[i], purl=upfile)  #寫入資料庫
                    unit.save()
                    i += 1
            return redirect('/album_adminfix/' + str(album.id) + '/')
        elif deletetype == 'update':  #更新相片說明
            photo = models.PhotoModel.objects.get(id=photoid)
            photo.psubject = request.POST.get('ap_subject', '')  #取得相片說明
            photo.save()  #存寫入資料庫
            return redirect('/album_adminfix/' + str(album.id) + '/')
        elif deletetype=='delete':  #刪除相片
            photo = models.PhotoModel.objects.get(id=photoid)
            os.remove(os.path.join(settings.MEDIA_ROOT, photo.purl ))  #刪除相片檔
            photo.delete()  #從資料庫移除
            return redirect('/album_adminfix/' + str(album.id) + '/')
    return render(request, "album_adminfix.html", locals())

#Google Map

def map_index(request):
	all=maplist.objects.all()  #取得所有景點
	return render(request, "map_index.html", locals())

def map_login(request):  #登入
	messages = ''  #初始時清除訊息
	if request.method == 'POST':  #如果是以POST方式才處理
		name = request.POST['username'].strip()  #取得輸入帳號
		password = request.POST['password']  #取得輸入密碼
		user1 = authenticate(username=name, password=password)  #驗證
		if user1 is not None:  #驗證通過
			if user1.is_active:  #帳號有效
				auth.login(request, user1)  #登入
				return redirect('/map_adminmain/')  #開啟管理頁面
			else:  #帳號無效
				message = '帳號尚未啟用！'
		else:  #驗證未通過
			message = '登入失敗！'
	return render(request, "map_login.html", locals())

def map_logout(request):  #登出
	auth.logout(request)
	return redirect('/map_index/')

def map_adminmain(request):  #管理首頁
	map_list = maplist.objects.all().order_by('-id')  #遞減排序取得所有景點
	paginator = Paginator(map_list, 6)  #每頁資料筆數
	page = request.GET.get('page')  #取得目前頁數
	try:
		maps = paginator.page(page)
	except PageNotAnInteger:  #若頁數非整數就顯示第1頁
		maps = paginator.page(1)
	except EmptyPage:  #若頁數超出範圍就顯示最後1頁
		maps = paginator.page(paginator.num_pages)
	return render(request, "map_adminmain.html", locals())

def map_adminadd(request):  # 新增景點
	if ('mapName' in request.POST):  # 按確定新增鈕
		name = request.POST['mapName']
		desc = request.POST['mapDesc']
		lat = request.POST['mapLat']
		lng = request.POST['mapLng']
		tel = request.POST['mapTel']
		addr = request.POST['mapAddr']
		rec = maplist(mapName=name, mapDesc=desc, mapLat=lat, mapLng=lng, mapTel=tel, mapAddr=addr)  # 建立資料記錄
		rec.save()  # 寫入資料表
		return redirect('/map_adminmain/')
	return render(request, "map_adminadd.html", locals())


def map_adminedit(request, editid=None):  # 修改景點資料
	if editid != None:  # 管理首頁按編輯鈕
		rec = maplist.objects.get(id=editid)  # 取得景點資料
		return render(request, "map_adminedit.html", locals())
	else:  # 按確定更新鈕
		editid1 = request.POST['editid']  # 取得景點編號
		rec = maplist.objects.get(id=editid1)  # 取得景點資料
		rec.mapName = request.POST['mapName']  # 取得景點欄位值
		rec.mapDesc = request.POST['mapDesc']
		rec.mapLat = request.POST['mapLat']
		rec.mapLng = request.POST['mapLng']
		rec.mapTel = request.POST['mapTel']
		rec.mapAddr = request.POST['mapAddr']
		rec.save()  # 寫入資料庫
		return redirect('/map_adminmain/')

def map_admindelete(request):  # 刪除景點
	delid = request.GET['id']  # 取得景點編號
	rec = maplist.objects.get(id=delid)  # 取得景點資料
	rec.delete()  # 刪除景點資料
	return redirect('/map_adminmain/')

#News

def news_index(request, pageindex=None):  #首頁
	global page1
	pagesize = 8
	newsall = models.NewsUnit.objects.all().order_by('-id')
	datasize = len(newsall)
	totpage = math.ceil(datasize / pagesize)
	if pageindex==None:
		page1 = 1
		newsunits = models.NewsUnit.objects.filter(enabled=True).order_by('-id')[:pagesize]
	elif pageindex=='1':
		start = (page1-2)*pagesize
		if start >= 0:
			newsunits = models.NewsUnit.objects.filter(enabled=True).order_by('-id')[start:(start+pagesize)]
			page1 -= 1
	elif pageindex=='2':
		start = page1*pagesize
		if start < datasize:
			newsunits = models.NewsUnit.objects.filter(enabled=True).order_by('-id')[start:(start+pagesize)]
			page1 += 1
	elif pageindex=='3':
		start = (page1-1)*pagesize
		newsunits = models.NewsUnit.objects.filter(enabled=True).order_by('-id')[start:(start+pagesize)]
	currentpage = page1
	return render(request, "news_index.html", locals())

def news_detail(request, detailid=None):  #詳細頁面
	unit = models.NewsUnit.objects.get(id=detailid)
	category = unit.catego
	ntitle = unit.ntitle
	pubtime = unit.pubtime
	nickname = unit.nickname
	message = unit.message
	unit.press += 1
	unit.save()
	return render(request, "news_detail.html", locals())

def news_login(request):  #登入
	messages = ''  #初始時清除訊息
	if request.method == 'POST':  #如果是以POST方式才處理
		name = request.POST['username'].strip()  #取得輸入帳號
		password = request.POST['password']  #取得輸入密碼
		user1 = authenticate(username=name, password=password)  #驗證
		if user1 is not None:  #驗證通過
			if user1.is_active:  #帳號有效
				auth.login(request, user1)  #登入
				return redirect('/news_adminmain/')  #開啟管理頁面
			else:  #帳號無效
				messages = '帳號尚未啟用！'
		else:  #驗證未通過
			messages = '登入失敗！'
	return render(request, "news_login.html", locals())

def news_logout(request):  #登出
	auth.logout(request)
	return redirect('/news_index/')

def news_adminmain(request, pageindex=None):  #管理頁面
	global page1
	pagesize = 8
	newsall = models.NewsUnit.objects.all().order_by('-id')
	datasize = len(newsall)
	totpage = math.ceil(datasize / pagesize)
	if pageindex==None:
		page1 = 1
		newsunits = models.NewsUnit.objects.order_by('-id')[:pagesize]
	elif pageindex=='1':
		start = (page1-2)*pagesize
		if start >= 0:
			newsunits = models.NewsUnit.objects.order_by('-id')[start:(start+pagesize)]
			page1 -= 1
	elif pageindex=='2':
		start = page1*pagesize
		if start < datasize:
			newsunits = models.NewsUnit.objects.order_by('-id')[start:(start+pagesize)]
			page1 += 1
	elif pageindex=='3':
		start = (page1-1)*pagesize
		newsunits = models.NewsUnit.objects.order_by('-id')[start:(start+pagesize)]
	currentpage = page1
	return render(request, "news_adminmain.html", locals())

def news_add(request):  #新增資料
	message = ''  #清除訊息
	category = request.POST.get('news_type', '')  #取得輸入的類別
	subject = request.POST.get('news_subject', '')
	editor = request.POST.get('news_editor', '')
	content = request.POST.get('news_content', '')
	ok = request.POST.get('news_ok', '')
	if subject=='' or editor=='' or content=='':  #若有欄位未填就顯示訊息
		message = '每一個欄位都要填寫...'
	else:
		if ok=='yes':  #根據ok值設定enabled欄位
			enabled = True
		else:
			enabled = False
		unit = models.NewsUnit.objects.create(catego=category, nickname=editor, ntitle=subject, message=content, enabled=enabled, press=0)
		unit.save()
		return redirect('/news_adminmain/')
	return render(request, "news_add.html", locals())

def news_edit(request, newsid=None, edittype=None):  #修改資料
	unit = models.NewsUnit.objects.get(id=newsid)  #讀取指定資料
	categories = ["公告", "更新", "活動", "其他"]
	if edittype == None:  #進入修改頁面,顯示原有資料
		type = unit.catego
		subject = unit.ntitle
		editor = unit.nickname
		content = unit.message
		ok = unit.enabled
	elif edittype == '1':  #修改完畢,存檔
		category = request.POST.get('news_type', '')
		subject = request.POST.get('news_subject', '')
		editor = request.POST.get('news_editor', '')
		content = request.POST.get('news_content', '')
		ok = request.POST.get('news_ok', '')
		if ok=='yes':
			enabled = True
		else:
			enabled = False
		unit.catego=category
		unit.nickname=editor
		unit.ntitle=subject
		unit.message=content
		unit.enabled=enabled
		unit.save()
		return redirect('/news_adminmain/')
	return render(request, "news_edit.html", locals())

def news_delete(request, newsid=None, deletetype=None):  #刪除資料
	unit = models.NewsUnit.objects.get(id=newsid)  #讀取指定資料
	if deletetype == None:  #進入刪除頁面,顯示原有資料
		type = str(unit.catego.strip())
		subject = unit.ntitle
		editor = unit.nickname
		content = unit.message
		date = unit.pubtime
	elif deletetype == '1':  #按刪除鈕
		unit.delete()
		return redirect('/news_adminmain/')
	return render(request, "news_delete.html", locals())

#introduction

def introduction(request):

	return render(request, "introduction.html", locals())