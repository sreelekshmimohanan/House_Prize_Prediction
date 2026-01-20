from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect,get_object_or_404 
# FILE UPLOAD AND VIEW
from  django.core.files.storage import FileSystemStorage
# SESSION
from django.conf import settings
from .models import *
from django.contrib import messages

def first(request):
    return render(request,'index.html')

def index(request):
    return render(request,'index.html')


def reg(request):
    return render(request,'register.html')


def addreg(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        phone=request.POST.get('phone')
        password=request.POST.get('password')
        ins=register(name=name,email=email,phone=phone,password=password)
        ins.save()
    return render(request,'register.html',{'message':"Successfully Registerd"})    




def login(request):
     return render(request,'login.html')
    



def addlogin(request):
    email=request.POST.get('email')
    password=request.POST.get('password')
    if email=='admin@gmail.com' and password =='admin':
        request.session['logint']=email
        request.session['role'] = 'admin'
        return render(request,'index.html')
    elif register.objects.filter(email=email,password=password).exists():
        user=register.objects.get(email=email,password=password)
        request.session['uid']=user.id
        request.session['role'] = 'user'
        return render(request,'index.html')
    elif Owner.objects.filter(email=email,password=password).exists():
        owner=Owner.objects.get(email=email,password=password)
        request.session['owner_id']=owner.id
        request.session['role'] = 'owner'
        return render(request,'index.html')
    else:
        return render(request,'login.html', {'error': 'Invalid credentials'})
    



def logout(request):
    session_keys=list(request.session.keys())
    for key in session_keys:
          del request.session[key]
    return redirect(first)

def viewuser(request):
    data=register.objects.all()
    return render(request,'viewuser.html',{'data':data})

def owner_reg(request):
    return render(request,'owner_register.html')

def add_owner_reg(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        address = request.POST.get('address', '')
        license_number = request.POST.get('license_number', '')
        if Owner.objects.filter(email=email).exists():
            return render(request, 'owner_register.html', {'error': 'Email already exists'})
        ins = Owner(name=name, email=email, phone=phone, password=password, address=address, license_number=license_number)
        ins.save()
        return render(request, 'owner_register.html', {'message': "Successfully Registered as Owner"})

def add_properties(request):
    if not request.session.get('owner_id'):
        return redirect('login')
    
    import ast
    import joblib
    import numpy as np
    import pandas as pd
    
    # Load mappings
    with open('ML/mapping_area_type.txt', 'r') as f:
        area_type_mapping = ast.literal_eval(f.read())
    with open('ML/mapping_HALL_KITCHEN.txt', 'r') as f:
        hall_kitchen_mapping = ast.literal_eval(f.read())
    with open('ML/mapping_location_new.txt', 'r') as f:
        location_mapping = ast.literal_eval(f.read())
    
    # Load model and scaler
    model = joblib.load('ML/model.joblib')
    scaler = joblib.load('ML/scaler.joblib')
    
    area_type_options = list(area_type_mapping.keys())
    hall_kitchen_options = list(hall_kitchen_mapping.keys())
    location_options = list(location_mapping.keys())
    
    print("Scaler feature names:", scaler.feature_names_in_)
    
    predicted_price = None
    form_data = {}
    price = form_data.get('price', '')
    
    if request.method == "POST":
        if 'predict' in request.POST:
            # Predict price
            area_type = request.POST.get('area_type')
            total_sqft = float(request.POST.get('total_sqft'))
            bath = int(request.POST.get('bath'))
            balcony = int(request.POST.get('balcony'))
            BHK = int(request.POST.get('BHK'))
            HALL_KITCHEN = request.POST.get('HALL_KITCHEN')
            location_new = request.POST.get('location_new')

            print("Input Values:", area_type, total_sqft, bath, balcony, BHK, HALL_KITCHEN, location_new)
            
            # Encode categoricals
            area_type_encoded = area_type_mapping[area_type]
            hall_kitchen_encoded = hall_kitchen_mapping[HALL_KITCHEN]
            location_encoded = location_mapping[location_new]

            print("Encoded Values:", area_type_encoded, hall_kitchen_encoded, location_encoded)
            
            # Prepare features in the order used in training: area_type, total_sqft, bath, balcony, BHK, HALL_KITCHEN, location_new
            features = pd.DataFrame([[area_type_encoded, total_sqft, bath, balcony, BHK, hall_kitchen_encoded, location_encoded]], 
                                   columns=['area_type', 'total_sqft', 'bath', 'balcony', 'BHK', 'HALL_KITCHEN', 'location_new'])
            
            # Scale features
            features_scaled = scaler.transform(features)
            
            # Predict
            predicted_price = model.predict(features_scaled)[0]

            print("Predicted Price:", predicted_price)

            if predicted_price < 1:
                predicted_price = 1
            
            return render(request, 'add_properties.html', {
                'area_type_options': area_type_options,
                'hall_kitchen_options': hall_kitchen_options,
                'location_options': location_options,
                'predicted_price': round(predicted_price, 2),
                'form_data': request.POST,  # To repopulate form
                'price': request.POST.get('price', '')
            })
        
        elif 'add_property' in request.POST:
            # Add property
            owner = Owner.objects.get(id=request.session['owner_id'])
            area_type = request.POST.get('area_type')
            total_sqft = request.POST.get('total_sqft')
            bath = request.POST.get('bath')
            balcony = request.POST.get('balcony')
            BHK = request.POST.get('BHK')
            HALL_KITCHEN = request.POST.get('HALL_KITCHEN')
            location_new = request.POST.get('location_new')
            price = request.POST.get('price', None)
            availability = request.POST.get('availability', '')
            
            property_obj = Property(
                owner=owner,
                area_type=area_type,
                total_sqft=float(total_sqft),
                bath=int(bath),
                balcony=int(balcony),
                BHK=int(BHK),
                HALL_KITCHEN=HALL_KITCHEN,
                location_new=location_new,
                price=float(price) if price else None,
                availability=availability
            )
            property_obj.save()
            return render(request, 'add_properties.html', {
                'message': 'Property added successfully!',
                'area_type_options': area_type_options,
                'hall_kitchen_options': hall_kitchen_options,
                'location_options': location_options,
                'form_data': form_data,
                'price': ''
            })
    
    return render(request, 'add_properties.html', {
        'area_type_options': area_type_options,
        'hall_kitchen_options': hall_kitchen_options,
        'location_options': location_options,
        'form_data': form_data,
        'price': price
    })

def view_owner_properties(request):
    if not request.session.get('owner_id'):
        return redirect('login')
    
    owner = Owner.objects.get(id=request.session['owner_id'])
    properties = Property.objects.filter(owner=owner)
    return render(request, 'view_owner_properties.html', {'properties': properties, 'owner': owner})

def view_properties(request):
    if not request.session.get('uid'):
        return redirect('login')
    
    properties = Property.objects.all()
    return render(request, 'view_properties.html', {'properties': properties})

def predict_price(request, property_id):
    if not request.session.get('uid'):
        return redirect('login')
    
    property_obj = get_object_or_404(Property, id=property_id)
    
    import ast
    import joblib
    import numpy as np
    import pandas as pd
    
    # Load mappings
    with open('ML/mapping_area_type.txt', 'r') as f:
        area_type_mapping = ast.literal_eval(f.read())
    with open('ML/mapping_HALL_KITCHEN.txt', 'r') as f:
        hall_kitchen_mapping = ast.literal_eval(f.read())
    with open('ML/mapping_location_new.txt', 'r') as f:
        location_mapping = ast.literal_eval(f.read())
    
    # Load model and scaler
    model = joblib.load('ML/model.joblib')
    scaler = joblib.load('ML/scaler.joblib')
    
    # Get data from property
    area_type = property_obj.area_type
    total_sqft = property_obj.total_sqft
    bath = property_obj.bath
    balcony = property_obj.balcony
    BHK = property_obj.BHK
    HALL_KITCHEN = property_obj.HALL_KITCHEN
    location_new = property_obj.location_new
    
    # Encode
    area_type_encoded = area_type_mapping[area_type]
    hall_kitchen_encoded = hall_kitchen_mapping[HALL_KITCHEN]
    location_encoded = location_mapping[location_new]
    
    # Features
    features = pd.DataFrame([[area_type_encoded, total_sqft, bath, balcony, BHK, hall_kitchen_encoded, location_encoded]], 
                           columns=['area_type', 'total_sqft', 'bath', 'balcony', 'BHK', 'HALL_KITCHEN', 'location_new'])
    
    # Scale
    features_scaled = scaler.transform(features)
    
    # Predict
    predicted_price = model.predict(features_scaled)[0]
    
    return render(request, 'predict_price.html', {
        'property': property_obj,
        'predicted_price': round(predicted_price, 2)
    })