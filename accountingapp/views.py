from django.shortcuts import render,HttpResponse,redirect
from accountingapp.models import listOfAll,listOfNames
from django.db.models import Q
from django.db.models import Sum 
from datetime import datetime, timedelta, date
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
import requests

# Create your views here.

def index(request):
    # temp create user directly:
    # login="padmavati"
    # password="123"
    # user = User.objects.create_user(username=login, password=password)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # If user is authenticated, log them in
            login(request,user)
            return redirect('/start')  # Redirect to dashboard on successful login
        else:
            # If authentication fails, display an error message
            return redirect('/')  # Redirect back to login page with error message
            error_message = 'wrong user or password'
            return render(request, 'index.html', {'error_message': error_message})
    else:
        # Render the login form
        return render(request, 'index.html')


def changepass(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            return render(request, "changepass.html")
        else:
            old_password = request.POST['oldpass']
            new_password = request.POST['newpass']
            confirm_password = request.POST['confirmpass']

            # Get the current user
            current_user = request.user

            # Check if the old password matches the user's current password
            if not check_password(old_password, current_user.password):
                error_message = 'The old password is incorrect.'
                return render(request, 'changepass.html', {'error_message': error_message})

            # Check if the new password and confirm password match
            if new_password != confirm_password:
                error_message = 'The new password and confirm password do not match.'
                return render(request, 'changepass.html', {'error_message': error_message})

            # Update the user's password
            current_user.set_password(new_password)
            current_user.save()

            # Update the user's session to prevent them from being logged out after password change
            update_session_auth_hash(request, current_user)

            # Redirect to a success page or any other page you want
            return redirect('/start')
    else:
        return redirect("/")


def start(request):
    if request.user.is_authenticated:
        return render(request,"index1.html")
    else:
        return redirect("/")

def customer(request):
    if request.user.is_authenticated:
        allcustomer=listOfNames.objects.filter(option='customer',user=request.user)
        context = {
            'allcustomer': [],
        }
        total_amt=0
        total_fine=0
        for current in allcustomer:
            currentcustomer=listOfAll.objects.filter(name_id=current)
            debit_totals = currentcustomer.filter(ledgeroption="debit").aggregate(
            debitamt=Sum('amount'),
            debitfine=Sum('fine')
            )
            credit_totals = currentcustomer.filter(ledgeroption="credit").aggregate(
            creditamt=Sum('amount'),
            creditfine=Sum('fine')
            )
            customer.amt =  round((credit_totals['creditamt'] or 0) - (debit_totals['debitamt'] or 0) ,2)
            customer.fine = round((credit_totals['creditfine'] or 0) -(debit_totals['debitfine'] or 0),2)
            context['allcustomer'].append({
                'name': current,
                'amt': customer.amt,
                'fine': customer.fine,
            })
            total_amt=total_amt+customer.amt
            total_fine=total_fine+customer.fine
        context['totalamt']=total_amt
        context['totalfine']=total_fine
        return render(request,"customer.html",context)

def createcustomer(request):
    if request.user.is_authenticated:
        if request.method=='GET':
            return render(request,'createcustomer.html')
        else:
            newcustomer = request.POST.get('name')
            mobile = request.POST.get('mobile')
            address = request.POST.get('address')
            option = request.POST.get('type')
            try:
                # Attempt to create a new customer record
                new_customer = listOfNames.objects.create(name=newcustomer, option=option, mobile=mobile, address=address,user=request.user)
                return redirect('/customer')
            except IntegrityError:
                # Handle the case where a customer with the same name already exists
                error_message = 'A customer with this name already exists.'
                return render(request, 'createcustomer.html', {'error_message': error_message})
    else:
        return redirect("/")
def detailsOfCustomer(request,name):
    if request.user.is_authenticated:
        current=listOfNames.objects.get(name=name,user=request.user,option="customer")
        currentcustomer=listOfAll.objects.filter(name_id=current).order_by('date') 
        # Handle form submission
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            else:
                # If end date is not provided, use current date
                end_date = date.today()
            
            # Filter records within the date range
            currentcustomer = currentcustomer.filter(date__range=[start_date, end_date])
        first_entry = currentcustomer.first()
        last_entry = currentcustomer.last()
        # Calculate debit and credit totals
        debit_totals = currentcustomer.filter(ledgeroption="debit").aggregate(
            debitamt=Sum('amount'),
            debitfine=Sum('fine')
        )

        credit_totals = currentcustomer.filter(ledgeroption="credit").aggregate(
            creditamt=Sum('amount'),
            creditfine=Sum('fine')
        )
        df=0
        cf=0
        dt=0
        ct=0
        if(debit_totals['debitfine'] is not None):
            df=round(debit_totals['debitfine'],3)
        if(credit_totals['creditfine'] is not None):
            cf=round(credit_totals['creditfine'],3)
        if(debit_totals['debitamt'] is not None):
                dt=round(debit_totals['debitamt'],2)
        if(credit_totals['creditamt'] is not None):
                ct=round(credit_totals['creditamt'],2)
        context = {}
        context['totaldebitfine'] = df
        context['totalcreditfine'] = cf
        context['totaldebitamt'] = dt
        context['totalcreditamt'] = ct
        if(len(currentcustomer) != 0):
            if (debit_totals['debitamt'] or 0) > (credit_totals['creditamt'] or 0):
                context['debitamtmore'] = round((debit_totals['debitamt'] or 0) - (credit_totals['creditamt'] or 0),2)
                context['creditamtmore']=0
            elif (credit_totals['creditamt'] or 0) > (debit_totals['debitamt'] or 0):
                context['creditamtmore'] = round((credit_totals['creditamt'] or 0) - (debit_totals['debitamt'] or 0),2)
                context['debitamtmore']=0
            else:
                context['debitamtmore']=0
                context['creditamtmore']=0

            if (debit_totals['debitfine'] or 0) > (credit_totals['creditfine'] or 0):
                context['debitfine'] = round((debit_totals['debitfine'] or 0) - (credit_totals['creditfine'] or 0),3)
                context['creditfine']=0
            elif (credit_totals['creditfine'] or 0) > (debit_totals['debitfine'] or 0):
                context['creditfine'] = round((credit_totals['creditfine'] or 0) - (debit_totals['debitfine'] or 0),3)
                context['debitfine']=0
            else:
                context['debitfine']=0
                context['creditfine']=0
        context['ledger_entries']=currentcustomer
        context['currentdetails']=current
        context['name']=name
        context['firstdate']=first_entry.date if first_entry else None
        context['lastdate']=last_entry.date if last_entry else None
        return render(request,'detailsofcustomer.html',context)
    else:
        return redirect("/")    


def addCustomerEntryDebit(request,name):
    if request.user.is_authenticated:
        if request.method=="GET":    
            context={}
            context['name']=name
            return render(request,'debitcustomer.html',context)
        else:
            currentname=name
            login=request.user
            name=listOfNames.objects.get(name=name,user=request.user,option="customer")
            date=request.POST['date']
            narration=request.POST['narration']
            weight=request.POST['weight']
            percentage=request.POST['percentage']
            rate=request.POST['rate']
            fine=request.POST['fine']
            amount=request.POST['amount']
            new=listOfAll.objects.create(login=login,date=date,narration=narration,weight=weight,percentage=percentage,rate=rate,fine=fine,ledgeroption="debit",ledger='customer',name_id=name,amount=amount)
            return redirect(f"/detailsOfCustomer/{currentname}")
    else:
        return redirect("/")
        

def addCustomerEntryCredit(request,name):
    if request.user.is_authenticated:
        if request.method=="GET":    
            context={}
            context['name']=name
            return render(request,'creditcustomer.html',context)
        else:
            currentname=name
            login=request.user
            name=listOfNames.objects.get(name=name,user=request.user,option="customer")
            date=request.POST['date']
            narration=request.POST['narration']
            weight=request.POST['weight']
            percentage=request.POST['percentage']
            rate=request.POST['rate']
            fine=request.POST['fine']
            amount=request.POST['amount']
            new=listOfAll.objects.create(login=login,date=date,narration=narration,weight=weight,percentage=percentage,rate=rate,fine=fine,ledgeroption="credit",ledger='customer',name_id=name,amount=amount)
            return redirect(f"/detailsOfCustomer/{currentname}")
    else:
        return redirect("/")


def supplier(request):
    if request.user.is_authenticated:
        allsupplier=listOfNames.objects.filter(option='supplier',user=request.user)
        context = {
            'allsupplier': [],
        }
        total_amt=0
        total_fine=0
        for current in allsupplier:
            currentsupplier=listOfAll.objects.filter(name_id=current)
            debit_totals = currentsupplier.filter(ledgeroption="debit").aggregate(
            debitamt=Sum('amount'),
            debitfine=Sum('fine')
            )
            credit_totals = currentsupplier.filter(ledgeroption="credit").aggregate(
            creditamt=Sum('amount'),
            creditfine=Sum('fine')
            )
            supplier.amt =  round((credit_totals['creditamt'] or 0) - (debit_totals['debitamt'] or 0),2) 
            supplier.fine = round((credit_totals['creditfine'] or 0) -(debit_totals['debitfine'] or 0),3)   
            context['allsupplier'].append({
                'name': current,
                'amt': supplier.amt,
                'fine': supplier.fine,
            })
            total_amt=total_amt+supplier.amt
            total_fine=total_fine+supplier.fine
        context['totalamt']=total_amt
        context['totalfine']=total_fine
        return render(request,"supplier.html",context)
    else:
        return redirect("/")

def createsupplier(request):
    if request.user.is_authenticated:
        if request.method=='GET':
            return render(request,'createsupplier.html')
        else:
            newsupplier=request.POST['name']
            mobile=request.POST['mobile']
            address=request.POST['address']
            option=request.POST['type']
            try:
                # Attempt to create a new supplier record
                new_supplier = listOfNames.objects.create(name=newsupplier, option=option, mobile=mobile, address=address,user=request.user)
                return redirect('/supplier')
            except IntegrityError:
                # Handle the case where a supplier with the same name already exists
                error_message = 'A supplier with this name already exists.'
                return render(request, 'createsupplier.html', {'error_message': error_message})
    else:
        return redirect("/")

def detailsOfSupplier(request,name):
    if request.user.is_authenticated:
        # name=listOfNames.objects.get(id=name)
        current=listOfNames.objects.get(name=name,user=request.user,option="supplier")
        currentsupplier=listOfAll.objects.filter(name_id=current).order_by('date')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            else:
                # If end date is not provided, use current date
                end_date = date.today()
            
            # Filter records within the date range
            currentsupplier = currentsupplier.filter(date__range=[start_date, end_date])
        first_entry = currentsupplier.first()
        last_entry = currentsupplier.last()    
        debit_totals = currentsupplier.filter(ledgeroption="debit").aggregate(
            debitamt=Sum('amount'),
            debitfine=Sum('fine')
        )

        credit_totals = currentsupplier.filter(ledgeroption="credit").aggregate(
            creditamt=Sum('amount'),
            creditfine=Sum('fine')
        )
        df=0
        cf=0
        dt=0
        ct=0
        if(debit_totals['debitfine'] is not None):
            df=round(debit_totals['debitfine'],3)
        if(credit_totals['creditfine'] is not None):
            cf=round(credit_totals['creditfine'],3)
        if(debit_totals['debitamt'] is not None):
                dt=round(debit_totals['debitamt'],2)
        if(credit_totals['creditamt'] is not None):
                ct=round(credit_totals['creditamt'],2)
        context = {}
        context['totaldebitfine'] = df
        context['totalcreditfine'] = cf
        context['totaldebitamt'] = dt
        context['totalcreditamt'] = ct
        if(len(currentsupplier) != 0):
            if (debit_totals['debitamt'] or 0) > (credit_totals['creditamt'] or 0):
                context['debitamtmore'] = round((debit_totals['debitamt'] or 0) - (credit_totals['creditamt'] or 0),2)
                context['creditamtmore']=0
            elif (credit_totals['creditamt'] or 0) > (debit_totals['debitamt'] or 0):
                context['creditamtmore'] = round((credit_totals['creditamt'] or 0) - (debit_totals['debitamt'] or 0),2)
                context['debitamtmore']=0
            else:
                context['debitamtmore']=0
                context['creditamtmore']=0

            if (debit_totals['debitfine'] or 0) > (credit_totals['creditfine'] or 0):
                context['debitfine'] = round((debit_totals['debitfine'] or 0) - (credit_totals['creditfine'] or 0),3)
                context['creditfine']=0
            elif (credit_totals['creditfine'] or 0) > (debit_totals['debitfine'] or 0):
                context['creditfine'] = round((credit_totals['creditfine'] or 0) - (debit_totals['debitfine'] or 0),3)
                context['debitfine']=0
            else:
                context['debitfine']=0
                context['creditfine']=0

        context['ledger_entries']=currentsupplier
        context['currentdetails']=current
        context['firstdate']=first_entry.date if first_entry else None
        context['lastdate']=last_entry.date if last_entry else None
        context['name']=name
        return render(request,'detailsofsupplier.html',context)
    else:
        return redirect("/")

def addSupplierEntryDebit(request,name):
    if request.user.is_authenticated:
        if request.method=="GET":    
            context={}
            context['name']=name
            return render(request,'debitsupplier.html',context)
        else:
            currentname=name
            login=request.user
            name=listOfNames.objects.get(name=name,user=request.user,option="supplier")
            date=request.POST['date']
            narration=request.POST['narration']
            weight=request.POST['weight']
            percentage=request.POST['percentage']
            rate=request.POST['rate']
            fine=request.POST['fine']
            amount=request.POST['amount']
            new=listOfAll.objects.create(login=login,date=date,narration=narration,weight=weight,percentage=percentage,rate=rate,fine=fine,ledgeroption="debit",ledger='supplier',name_id=name,amount=amount)
            return redirect(f"/detailsOfSupplier/{currentname}")
    else:
        return redirect("/")        

def addSupplierEntryCredit(request,name):
    if request.user.is_authenticated:
        if request.method=="GET":    
            context={}
            context['name']=name
            return render(request,'creditsupplier.html',context)
        else:
            currentname=name
            login=request.user
            name=listOfNames.objects.get(name=name,user=request.user,option="supplier")
            date=request.POST['date']
            narration=request.POST['narration']
            weight=request.POST['weight']
            percentage=request.POST['percentage']
            rate=request.POST['rate']
            fine=request.POST['fine']
            amount=request.POST['amount']
            new=listOfAll.objects.create(login=login,date=date,narration=narration,weight=weight,percentage=percentage,rate=rate,fine=fine,ledgeroption="credit",ledger='supplier',name_id=name,amount=amount)
            return redirect(f"/detailsOfSupplier/{currentname}")
    else:
        return redirect("/")

def searchcustomer(request):
    if request.user.is_authenticated:
        query = request.GET.get('query', '')  # Get the query parameter from the request
        allcustomers = listOfNames.objects.filter(name__icontains=query,option="customer",user=request.user)  # Filter names using icontains
        context = {
            'allcustomer': [],
        }
        total_amt=0
        total_fine=0
        for current in allcustomers:
            currentcustomer=listOfAll.objects.filter(name_id=current)
            debit_totals = currentcustomer.filter(ledgeroption="debit").aggregate(
            debitamt=Sum('amount'),
            debitfine=Sum('fine')
            )
            credit_totals = currentcustomer.filter(ledgeroption="credit").aggregate(
            creditamt=Sum('amount'),
            creditfine=Sum('fine')
            )
            amt=0
            fine=0
            if(amt is not None):
                amt = round(amt, 2)
            if(fine is not None):
                fine = round(fine, 3)
            customer.amt =  round((credit_totals['creditamt'] or 0) - (debit_totals['debitamt'] or 0),2 )
            customer.fine = round((credit_totals['creditfine'] or 0) -(debit_totals['debitfine'] or 0),3 )
            context['allcustomer'].append({
                'name': current,
                'amt': customer.amt,
                'fine': customer.fine,
            })
            total_amt=total_amt+customer.amt
            total_fine=total_fine+customer.fine
        context['total_amt'] = round(total_amt, 2)
        context['total_fine'] = round(total_fine, 3)
        return render(request,"customer.html",context)
    else:
        return redirect("/")

def searchsupplier(request):
    if request.user.is_authenticated:
        query = request.GET.get('query', '')  # Get the query parameter from the request
        allsupplier = listOfNames.objects.filter(name__icontains=query,option="supplier",user=request.user)  # Filter names using icontains
        context = {
            'allsupplier': [],
        }
        total_amt=0
        total_fine=0
        for current in allsupplier:
            currentsupplier=listOfAll.objects.filter(name_id=current)
            debit_totals = currentsupplier.filter(ledgeroption="debit").aggregate(
            debitamt=Sum('amount'),
            debitfine=Sum('fine')
            )
            credit_totals = currentsupplier.filter(ledgeroption="credit").aggregate(
            creditamt=Sum('amount'),
            creditfine=Sum('fine')
            )
            amt=0
            fine=0
            if(amt is not None):
                amt = round(amt, 2)
            if(fine is not None):
                fine = round(fine, 3)
            supplier.amt =  round((credit_totals['creditamt'] or 0) - (debit_totals['debitamt'] or 0),2 )
            supplier.fine = round((credit_totals['creditfine'] or 0) -(debit_totals['debitfine'] or 0),3)
            context['allsupplier'].append({
                'name': current,
                'amt': supplier.amt,
                'fine': supplier.fine,
            })
            total_amt=total_amt+supplier.amt
            total_fine=total_fine+supplier.fine
        context['total_amt'] = round(total_amt, 2)
        context['total_fine'] = round(total_fine, 3)
        return render(request,"supplier.html",context)
    else:
        return redirect("/")

def edit_entry(request, entry_id):
    if request.user.is_authenticated:
        context={}
        entry=listOfAll.objects.get(id=entry_id)
        if request.method == 'GET':
            date_obj = entry.date
            formatted_date = date_obj.strftime("%b. %d, %Y")  # Format the date as needed
            context['current'] = entry
            context['date_obj'] = formatted_date  # Add the formatted date to the context
            return render(request, "update.html", context)
        else:
            pass
            # Update the entry with new values from the form
            entry_id = request.POST['id']
            entry=listOfAll.objects.get(id=entry_id)
            entry.date = entry.date
            entry.narration = request.POST['narration']
            entry.weight = request.POST['weight']
            entry.percentage = request.POST['percentage']
            entry.rate = request.POST['rate']
            entry.fine = request.POST['fine']
            entry.amount = request.POST['amount']
            value=entry.ledger
            # Save the updated entry
            entry.save()
            # Redirect to the details page or wherever appropriate
        if(value=="customer"):
            return redirect(f"/detailsOfCustomer/{entry.name_id.name}")
        else:
            return redirect(f"/detailsOfSupplier/{entry.name_id.name}")
    else:
        return redirect("/")

def delete(request,id):
    if request.user.is_authenticated:
        entry=listOfAll.objects.get(id=id)
        value=entry.ledger
        entry.delete()
        if(value=="customer"):
            return redirect(f"/detailsOfCustomer/{entry.name_id.name}")
        else:
            return redirect(f"/detailsOfSupplier/{entry.name_id.name}")
    else:
        return redirect("/")

def deleteuser(request,name):
    if request.user.is_authenticated:
        entry=listOfNames.objects.get(name=name,user=request.user,option="customer")
        entry.delete()
        return redirect("/customer")
    else:
        return redirect("/")

def deletesupplier(request,name):
    if request.user.is_authenticated:
        entry=listOfNames.objects.get(name=name,user=request.user,option="supplier")
        entry.delete()
        return redirect("/supplier")
    else:
        return redirect("/")

def updatecustomer(request):
    if request.user.is_authenticated:
        name = request.GET.get('name')  # Retrieve the value of 'name' from the query parameters
        customer = listOfNames.objects.get(name=name,option="customer",user=request.user)
        
        # Update the customer's mobile and address
        customer.mobile = request.GET.get('mobile')
        customer.address = request.GET.get('address')
        customer.save()
        return redirect(f"/detailsOfCustomer/{name}")
    else:
        return redirect("/")

def updatesupplier(request):
    if request.user.is_authenticated:
        name = request.GET.get('name')  # Retrieve the value of 'name' from the query parameters
        supplier = listOfNames.objects.get(name=name,option="supplier",user=request.user)
        
        # Update the customer's mobile and address
        supplier.mobile = request.GET.get('mobile')
        supplier.address = request.GET.get('address')
        supplier.save()
        return redirect(f"/detailsOfSupplier/{name}")
    else:
        return redirect("/")

def logoutuser(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("/")
    else:
        return redirect("/")

def whatsapp(request,number):
        # Assuming you have a form or some data with recipient phone number and message
    recipient_number = request.POST.get('recipient_number')
    message = request.POST.get('message')

        # Construct the WhatsApp API URL with the recipient's phone number and message
    url = "https://api.whatsapp.com/send?phone={}&text={}".format(number, message)

        # Optionally, you can use the requests library to make a GET request to the WhatsApp API URL
    response = requests.get(url)

        # Check if the request was successful
    if response.status_code == 200:
            # Handle success (e.g., return a success message)
        return HttpResponse("WhatsApp message sent successfully!")
    else:
            # Handle failure (e.g., return an error message)
        return HttpResponse("Failed to send WhatsApp message.")
