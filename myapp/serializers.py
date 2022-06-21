from rest_framework import serializers
from .models import*
from django.contrib.auth.hashers import make_password


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','password','role','mobile']
        
             
    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super(UserCreateSerializer, self).create(validated_data)
    
class UserLoginSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(max_length=30)
    class Meta:
        model=User
        fields=['email','password']  
  
class EditUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['first_name','last_name','mobile']
        
class ViewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['email','role','mobile','firat_name','last_name']
        
        
class AddProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['product_name','category','quantity','price','pic','description']
        
        
class EditProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['product_name','category','quantity','price','pic','description']
        
class ViewProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields=['product_name','category','quantity','price','pic','description']
        
class BuyerIndexSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'
        
class AddCartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Mycart
        fields=['quantity']
    
class MyCartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Mycart
        fields=['product','quantity']
        
      
class EditCartSerializer(serializers.ModelSerializer):
    class Meta:
        model=Mycart
        fields=['quantity']
        
class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model=Buyproduct
        fields=['addres','payment_method']
        
        
class BuyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Buyproduct
        fields=['addres','payment_method','quantity']

class MyBuyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Buyproduct
        fields='__all__'
    
class EditMyBuyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Buyproduct
        fields=['addres','quantity']
        