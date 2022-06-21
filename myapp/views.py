from django.shortcuts import render
from .models import*
from .serializers import*
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import*
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import*
from rest_framework import status
from django.contrib.auth.hashers import make_password


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
    
@api_view(['GET'])
def index(request):
    api_url={
        '':'index/',
        'register':'/register/',
        'login':'/login/',
        'verifay':'/verifay/id',
        'admin-index':'/admin-index/',
        'edit-profile':'/edit-profile/',
        'add-product':'/add-product/',
        'my-product':'/my-product/',
        'edit-product':'/edit-product/id',
        'delete-product':'/delete-product/id',
        'buyer-index':'/buyer-index/',
        'one-product':'/one-product/',
        'add-cart':'/add-cart/product-id',
        'my-cart':'/my-cart/',
        'edit-cart':'/edit-cart/id',
        'delete-cart':'/delete-cart/id',
        'checkout':'/checkout/',
        'buy-product/':'/buy-product/product-id',
        'my-buy':'/my-buy/',
        'edit-buyproduct':'/edit-buyproduct/id'
    }
    return Response(api_url)

class CreateUserView(GenericAPIView):
    serializer_class=UserCreateSerializer
    queryset=User.objects.all()
    
    def post(self,request):
        serializer=UserCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'})
    
class LoginUserView(GenericAPIView):
    serializer_class=UserLoginSerializer
    queryset=User.objects.all()
    
    def post(self,request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(email=email, password=password)
            if user is not None:
                if user.role == 'seller':
                    if user.verification == True: 
                        token = get_tokens_for_user(user)
                        return Response({'token':token,'status':status.HTTP_200_OK,'msg':'login Sucessfully'})
                    else:
                        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'your account not verifay'})
                else:
                    token = get_tokens_for_user(user)
                    return Response({'token':token,'status':status.HTTP_200_OK,'msg':'login Sucessfully'})  
            else:
                return Response({'status':status.HTTP_404_NOT_FOUND,'msg':"invalid email and password "})
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class AdminIndexView(ListAPIView):
    permission_classes=[IsAdminUser]
    serializer_class=ViewUserSerializer
    queryset=User.objects.all()
    
    
class SellerVerificationView(GenericAPIView):
    permission_classes=[IsAdminUser]
    
    def get(self,request,pk):
        user=User.objects.get(id=pk)
        if user.role == 'seller':
            user.verification = True
            user.save()
            return Response({'msg':'seller Verifay'})
        else:
            return Response({'msg':'Please enter only seller id'})   
        
class EditUserView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditUserSerializer
    queryset=User.objects.all() 
    
    def put(self,request):
        uid=User.objects.get(id=request.user.id)
        serializer=EditUserSerializer(instance=uid,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'}) 
    

#----------------------------------------------------SELLER----------------------------------------

class AddProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddProductSerializer
    queryset=Product.objects.all()
    
    def post(self,request):
        serializer=AddProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response({'data':serializer.data,'status':status.HTTP_200_OK,'msg':'product add for selling'})
        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'})

class ViewProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=ViewProductSerializer
    
    def get(self,request):
        pro=Product.objects.filter(seller=request.user)
        serializer=ViewProductSerializer(pro,many=True)
        return Response(serializer.data)
     
class EditProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditProductSerializer
    queryset=Product.objects.all()
    
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
    
    def put(self,request,pk):
        pro=self.get_object(pk=pk)
        if pro.seller == request.user:
            serializer=EditProductSerializer(instance=pro,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'data':serializer.data,'status':status.HTTP_200_OK,'msg':'your product Update'})
            return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'})
        return Response('you cannot edit other seller product')

class DeleteProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
   
    def get(self,request,pk):
        pro=self.get_object(pk=pk)
        if pro.seller == request.user:
            serializer=ViewProductSerializer(pro)
            return Response(serializer.data)
        else:
            return Response('you cannot show other seller product details')
        
    def delete(self,request,pk):
        pro=self.get_object(pk=pk)
        if pro.seller == request.user:
            pro.delete()
            return Response('your product delete')
        else:
            return Response('you cannot delete other seller product')
        
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>Buyer>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class BuyerIndexView(ListAPIView):
    serializer_class=BuyerIndexSerializer
    queryset=Product.objects.all()
    
class OneProductView(GenericAPIView):
    serializer_class=BuyerIndexSerializer
    queryset=Product.objects.all()
    
    def get_object(self, pk):
        try:
            return Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            raise Http404
   
    def get(self,request,pk):
        pro=self.get_object(pk=pk)
        serializer=BuyerIndexSerializer(pro)
        return Response(serializer.data)

class AddCartView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddCartSerializer
    
    def post(self,request,pk):
        pro=Product.objects.get(id=pk)
        serializer=AddCartSerializer(data=request.data)
        if serializer.is_valid():
            quantity=serializer.validated_data.get('quantity')
            if int(quantity) > 0:
                if pro.quantity >= int(quantity):
                    serializer.save(user=request.user,product=pro)
                    return Response({'status':status.HTTP_200_OK,'msg':'product add your cart','data':serializer.data})
                return Response('your quantity in more then available quantity')
            return Response('please ehter one or more quantity')
        else:
            return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})
        
class MyCartView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MyCartSerializer
    
    def get(self,request):
        cart=Mycart.objects.filter(user=request.user)
        serializer=MyCartSerializer(cart,many=True)
        return Response(serializer.data)  
    
class EditCartView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditCartSerializer
    
    def get_object(self, pk):
        try:
            return Mycart.objects.get(pk=pk)
        except Mycart.DoesNotExist:
            raise Http404
        
    def put(self,request,pk):
        cart=self.get_object(pk=pk)
        if cart.user == request.user:
            serializer=EditCartSerializer(instance=cart,data=request.data)
            if serializer.is_valid():
                quantity=serializer.validated_data.get('quantity')
                if int(quantity) > 0:
                    if cart.pro.quantity >= int(quantity):
                        serializer.save()
                        return Response({'status':status.HTTP_200_OK,'msg':'your cart update','data':serializer.data})
                    return Response('your quantity in more then available quantity')
                return Response('please ehter one or more quantity')
            else:
                return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})
        else:
            return Response({'msg':'you cannot edit other cart'})        
        
class DeleteCartView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Mycart.objects.get(pk=pk)
        except Mycart.DoesNotExist:
            raise Http404
        
    def delete(self,request,pk):
        cart=self.get_object(pk=pk)
        if cart.user == request.user:
            cart.delete()
            return Response('Your cart deleted')
        else:
            return Response('you cannot delete other user cart')

class CheckoutView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=CheckoutSerializer
    
    def post(self,request):
        user=request.user
        mycart=Mycart.objects.filter(user=user)      
        # total_amount=0.0
        # for i in mycart:
        #     total_amount += i.product.quantity * i.product.price
        
        for i in mycart:
            if i.product.quantity >= i.quantity:
                serializer=CheckoutSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save(user=user,
                                    product=i.product,
                                    total_amount=i.total_cost,
                                    quantity=i.quantity)
                    i.product.quantity -= i.quantity
                    i.product.save()
                    i.delete()
                else:
                    return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})
            else:
                return Response('your quantity in more then available quantity')
        return Response({'status':status.HTTP_200_OK,'msg':'you buy product successfully'})

class BuyProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=BuyProductSerializer
    
    def post(self,request,pk):
        pro=Product.objects.get(id=pk)
        serializer=BuyProductSerializer(data=request.data)
        if serializer.is_valid():
            quantity=serializer.validated_data.get('quantity')
            amount= int(quantity) * pro.price
            if int(quantity) > 0:
                if pro.quantity >= int(quantity):
                    serializer.save(user=request.user,product=pro,total_amount=amount)
                    pro.quantity -= int(quantity)
                    pro.save()
                    return Response({'status':status.HTTP_200_OK,'msg':'you buy product successfully'})
                else:
                    return Response('your quantity in more then available quantity')
            else:
                return Response('please enter valid qunantity')
        else:
            print(serializer.errors)
            return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})
        
        
class MyBuyProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=MyBuyProductSerializer
    
    def get(self,request):
        my=Buyproduct.objects.filter(user=request.user)
        serializer=MyBuyProductSerializer(my,many=True)
        return Response(serializer.data)
    
class EditMyBuyProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditMyBuyProductSerializer
    
    def get_object(self, pk):
        try:
            return Buyproduct.objects.get(pk=pk)
        except Buyproduct.DoesNotExist:
            raise Http404
        
    def put(self,request,pk):
        pro=self.get_object(pk=pk)
        if pro.user == request.user:
            if pro.status == 'pending' or pro.status == 'packing':
                serializer=EditMyBuyProductSerializer(instance=pro,data=request.data)
                if serializer.is_valid():
                    quanttiy=int(serializer.validated_data.get('quantity'))
                    if quanttiy > 0:
                        if  pro.product.quantity >= quanttiy:
                            pro.product.quantity += quanttiy
                            pro.product.save()
                            serializer.save()
                            pro.product.quantity -= quanttiy
                            pro.product.save()
                            return Response({'status':status.HTTP_200_OK,'msg':'your buy product update'})
                        else:
                            return Response('your quantity in more then available quantity')
                    else:
                        return Response('please enter valid qunantity')
                else:
                    return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'please enter the valid data'})
            else:
                return Response('your ordered is ready so you cannot edit')
        else:
            return Response('you cannot edit other user ordered')
                    
                    
                        

    
    
            
                
                
                    
                    
                
            
        
             
        
        