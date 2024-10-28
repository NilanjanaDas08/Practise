from django.shortcuts import render,redirect
from .models import User,Task
from django.http import HttpResponse
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password,check_password
import random
from django.utils import timezone


# Create your views here.
def register(request):
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        email=request.POST.get('email')
        password=request.POST.get('password')
        print(f"Email: {email}, Password: {password}") 
        if User.objects.filter(email=email).exists():
            return HttpResponse("Already Exists")
        else:
            hashed_password=make_password(password)
            User.objects.create(first_name=first_name,last_name=last_name,email=email,password=hashed_password)
            return redirect('login')
    return render(request,'register.html')

'''def login(request):
    config={}
    if 'user' in request.session:
        return redirect('task_list')
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user=User.objects.get(email=email)
            if user.check_password(password):

           # if check_password(password,user.password):
                request.session['user']={
                    'id':user.id,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'email':user.email
                        }
                print("Password is correct, redirecting to task_list")
                return redirect('task_list')
        except:
            config['errors']="Invalid email or password"
    return render(request,'login.html',config)'''

def login(request):
    config={}
    if 'user' in request.session:
        return redirect('task_list')
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        print(f"Email: {email}, Password: {password}") 
        try:
            user=User.objects.get(email=email)
            #Generate otp
            otp_code=f"{random.randint(100000,999999)}"
            otp_expiration = timezone.now() + timezone.timedelta(minutes=5)
            if check_password(password, user.password):
                # Store OTP and expiration in session
                request.session['otp_code'] = otp_code
                request.session['otp_expiration'] = otp_expiration.isoformat()
                request.session['user_email'] = email  # Store email for OTP verification
                
                # Send OTP email
                send_mail(
                    "Your OTP Code",
                    f"Your OTP code is {otp_code}. It is valid for 5 minutes.",
                    "from@example.com",
                    [email],
                    fail_silently=False,
                )
                 
                return redirect('verify_otp')
            else:
                print("Password is incorrect")
        except User.DoesNotExist:
            config['errors']="Invalid email or password"
    return render(request,'login.html',config)



def verify_otp(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp_code")
        stored_otp = request.session.get("otp_code")
        stored_expiration = request.session.get("otp_expiration")
        
        # Convert stored expiration to a datetime object
        if stored_expiration:
            stored_expiration = timezone.datetime.fromisoformat(stored_expiration)
        
        # Check if OTP matches and is still valid
        if (
            stored_otp == input_otp and
            stored_expiration and
            timezone.now() < stored_expiration
        ):
            # OTP is valid, log the user in
            user = User.objects.get(email=request.session['user_email'])
            request.session['user'] = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email
            }
            
            # Clear OTP session data
            request.session.pop("otp_code", None)
            request.session.pop("otp_expiration", None)
            request.session.pop("user_email", None)
            
            return redirect('task_list')
        else:
            return HttpResponse("Invalid or expired OTP.")
    
    return render(request, "verify_otp.html")



def task_list(request):
    user_info=request.session['user']
    user_id=user_info['id']
    user_instance=User.objects.get(id=user_id)
    tasks=Task.objects.filter(user=user_instance)
    if request.method=='POST':
        name=request.POST.get('name')
        if name:
            if Task.objects.filter(name=name,user=user_instance).count()>0:
                return HttpResponse("Already exists")
            else:
                Task.objects.create(name=name,user=user_instance)
                return redirect('task_list')
    return render(request,'task_list.html',{'tasks':tasks,'user_info':user_info})

def mark_as_done(request,task_id):
    task=Task.objects.get(id=task_id)
    task.status='COMPLETED' if task.status=='PENDING' else 'PENDING'
    task.save()
    return redirect('task_list')

def delete_task(request,task_id):
    Task.objects.get(id=task_id).delete()
    return redirect('task_list')

def logout(request):
    try:
        del request.session['user']
    except:
        pass
    return redirect('login')