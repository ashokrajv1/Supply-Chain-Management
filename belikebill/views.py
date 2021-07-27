import cx_Oracle
from django.http import HttpResponse
from django.contrib import messages
from .forms import UserRegisterForm
from django.shortcuts import render,redirect
from datetime import datetime

# Create your views here.
login_=False
ide=1
usr = None
ip='localhost'
port='1521'
ser='xe'
u='system'
p='1234'



def register(request):
	global ip,port,ser,u,p
	if request.method == 'POST':
		dsn_tns = cx_Oracle.makedsn(ip, port, service_name=ser) 
		conn = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
		c = conn.cursor()
		form = UserRegisterForm(request.POST)	
		if form.is_valid():
			form.save()
			username=form.cleaned_data.get('username')
			emailid=form.cleaned_data.get('email')
			password=form.cleaned_data.get('password1')
			c.prepare("insert into users(username,emailid,password) values(:username,:emailid,:password1)")
			c.execute(None,{'username':username,'emailid':emailid,'password1':password})
			conn.commit()
			conn.close()
			messages.success(request,f'Account created for {username}!')
			return redirect('Bill-home')
	else:
		form = UserRegisterForm()
	return render(request,'users/register.html',{'form' : form})
	

def login(request):
	global ip,port,ser,u,p
	if request.method=='POST':
		global login_
		dsn_tns = cx_Oracle.makedsn(ip, port, service_name=ser) 
		conn = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
		cx = conn.cursor()
		username=request.POST.get('username')
		global usr
		password=request.POST.get('password')
		cx.prepare("select password from users where username = :usr")
		cx.execute(None,{'usr':username})
		flag=0
		for i in cx:
			if password==i[0]:
				flag=True
		if flag==True:
			login_=True
			usr = username
			messages.success(request,f'Login Success {username}!')
			return redirect('Bill-home')
		else:
			messages.error(request,f'Login denied!')
			return redirect('Bill-home')	
		conn.close()	
	return render(request,'users/login.html')


def logout(request):
	global ip,port,ser,u,p
	global login_
	global usr
	login_=False
	usr = None
	messages.success(request,f'Logout Success')
	return redirect('Bill-home')

def home(request):	
	global ip,port,ser,u,p
	if login_== True:
		return render(request,'belikebill/home.html',{'username':usr})
	else:
		return redirect('login')

def addsupplier(request):
	global ip,port,ser,u,p
	if login_==True:
		if request.method=='POST':
			global usr
			dsn_tns = cx_Oracle.makedsn(ip, port, service_name=ser) 
			conn = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
			cx = conn.cursor()
			supplier={}
			for i in ['suppliername','address','phone','gst']:
				supplier[i]=request.POST.get(i)
			supplier['usr']=usr
			cx.prepare("insert into supplier values(:suppliername,:phone,:address,:gst,:usr)")
			cx.execute(None,supplier)
			conn.commit()
			conn.close()
			messages.success(request,'Supplier {} added!'.format(supplier['suppliername']))
			return redirect('addsupplier')
		else:
			return render(request,'belikebill/addsupplier.html',{'username':usr})
	else:
		return redirect('login')

bill=[]
total=0

def billing(request):
	global ip,port,ser,u,p
	if login_==True:
		global total
		global bill
		product={}
		if request.POST.get('print')==None and request.POST.get('name') != None:
			for i in ['name','quantity']:
				product[i] = request.POST.get(i)
			product['quantity']=int(product['quantity'])
			flag=0
			flag1=0
			dsn_tns = cx_Oracle.makedsn(ip, port, service_name=ser) 
			conn = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
			cx = conn.cursor()
			cx.prepare('select * from product where username=:usr and name=:name')
			cx.execute(None,{'usr':usr,'name':product['name']})
			for i in cx:
				if i[2]>=product['quantity']:
					product['rate']=i[1]
					product['total']=i[1]*product['quantity']
					total+=product['total']
					flag1=1
				flag=1
			if flag==0:
				messages.error(request,'Product {} doesnt exist'.format(product['name']))
			elif flag1==0:
				messages.error(request,'Quantity isnt sufficient')
			else:
				bill.append(product)
			conn.close()
			return render(request,'belikebill/billing.html',{'username':usr})
		elif request.POST.get('name')!=None:
			for i in ['name','quantity']:
				product[i] = request.POST.get(i)
			product['quantity']=int(product['quantity'])
			flag=0
			dsn_tns = cx_Oracle.makedsn(ip, port, service_name=ser) 
			conn = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
			cx = conn.cursor()
			cx.prepare('select * from product where username=:usr and name=:name')
			cx.execute(None,{'usr':usr,'name':product['name']})
			for i in cx:
				if i[2]>=product['quantity']:
					product['rate']=i[1]
					product['total']=i[1]*product['quantity']
					total+=product['total']
					flag1=1
				flag=1
			if flag==0:
				messages.error(request,'Product {} doesnt exist'.format(product['name']))
			elif flag1==0:
				messages.error(request,'Quantity isnt sufficient')
			else:
				bill.append(product)
				bill1=[]
				for i in bill:
					bill1.append(i)
				global ide
				bill=[]
				billinfo={'bill':bill1,'username':usr,'total':total,'date':datetime.now().strftime('%d/%m/%y'),'id':ide}
				ide+=1
				return render(request,'belikebill/bill.html',billinfo)
			return render(request,'belikebill/billing.html')
		else:
			return render(request,'belikebill/billing.html',{'username':usr})
	else:
		return redirect('login')


def inventory(request):
	global ip,port,ser,u,p
	if login_==True:
		if request.method=='POST':
			global usr
			dsn_tns = cx_Oracle.makedsn(ip, port, service_name=ser) 
			conn1 = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
			conn = cx_Oracle.connect(user=u, password=p, dsn=dsn_tns) 
			cx = conn.cursor()
			c = conn1.cursor()
			product={}
			for i in ['hsn','mrp','stock','name','supplier']:
				product[i]=request.POST.get(i)

			product['hsn']=int(product['hsn'])
			product['mrp']=int(product['mrp'])
			product['stock']=int(product['stock'])
			product['usr']=usr
			c.prepare('select name from supplier where username=:usr and name=:sn')
			c.execute(None,{'usr':usr,'sn':product['supplier']})
			flag=0
			for i in c:
				flag=1
			if flag==1:
				cx.prepare("insert into product(hsn,mrp,stock,name,username,supplier) values(:hsn,:mrp,:stock,:name,:usr,:supplier)")
				cx.execute(None,product)
				conn.commit()
				messages.success(request,'Product Added {} added!'.format(product['name']))
			else:
				messages.error(request,'Supplier {} doesnt exist!'.format(product['supplier']))
			conn.close()
			conn1.close()
			return redirect('inventory')
		else:
			return render(request,'belikebill/inventory.html',{'username':usr})
	else:
		return redirect('login')