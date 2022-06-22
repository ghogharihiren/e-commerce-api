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
from rest_framework.filters import SearchFilter
import random
from django.conf import settings
from django.core.mail import send_mail


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
        'user-delete':'/user-delete/id',
        'admin-index':'/admin-index/',
        'edit-profile':'/edit-profile/',
        'seller-index':'/seller-index/',
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
        'edit-buyproduct':'/edit-buyproduct/id',
        'cancel-ordered':'/cancel-ordered/id',
        'edit-status':'/edit-status/id',
        'search':'/search/',
        'forgot-password':'/forgot-password/',
        'change-password':'/change-password/',
    }
    return Response(api_url)

class CreateUserView(GenericAPIView):
    serializer_class=UserCreateSerializer
    queryset=User.objects.all()
    
    def post(self,request):
        serializer=UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status':status.HTTP_200_OK,'msg':'Your account create','data':serializer.data})
        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'})
    
class LoginUserView(GenericAPIView):
    serializer_class=UserLoginSerializer
    queryset=User.objects.all()
    
    def post(self,request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
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
    
class ForgotPasswordView(GenericAPIView):
    serializer_class=ForgotPasswordSerializer
    
    def post(self,request):
        serializer=ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email=serializer.validated_data.get('email')
            if User.objects.filter(email=email).exists():
                user=User.objects.get(email=email)
                password = ''.join(random.choices('qwyertovghlk34579385',k=8))
                subject="Rest Password"
                message = f"""Hello {user.email},Your New password is {password}"""
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email,]
                send_mail( subject, message, email_from, recipient_list )
                user.password=make_password(password)
                user.save()
                return Response('your new password send')
            else:
                return Response('enter your email')
        else:
            return Response('enter the valid data')

    
class UserChangePasswordview(GenericAPIView):
    serializer_class=ChangePasswordSerializer
    permission_classes=[IsAuthenticated]
    
    def put(self,request):
        user=User.objects.get(id=request.user.id)
        serializer=ChangePasswordSerializer(instance=user,data=request.data)
        if serializer.is_valid():
            password=serializer.validated_data.get('password')
            serializer.save(password=make_password(password))
            return Response('your password change')
        else:
            return Response('enter the valid data')
        

        
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
            return Response({'status':status.HTTP_200_OK,'msg':'your account update','data':serializer.data})
        return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid data'}) 
    
class DeleteUserView(GenericAPIView):
    permission_classes=[IsAdminUser]
    
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404
    
    def put(self,request,pk):
        pro=self.get_object(pk=pk)
        pro.delete()
        return Response('user delete')
    

#----------------------------------------------------SELLER----------------------------------------

class SellerIndexView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get(self,request):
        l=[]
        all=Buyproduct.objects.all()
        for i in all:
            if i.product.seller == request.user:
                l.append(i)
        serializer=SellerIndexSerializer(l,many=True)
        return Response(serializer.data)

class AddProductView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=AddProductSerializer
    queryset=Product.objects.all()
    
    def post(self,request):
        serializer=AddProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(seller=request.user)
            return Response({'status':status.HTTP_200_OK,'msg':'product add for selling','data':serializer.data})
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
                return Response({'status':status.HTTP_200_OK,'msg':'your product Update','data':serializer.data})
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
        
class EditStatusView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=EditStatusSerializer
    
    def get_object(self, pk):
        try:
            return Buyproduct.objects.get(pk=pk)
        except Buyproduct.DoesNotExist:
            raise Http404
        
    def put(self,request,pk):
        pro=self.get_object(pk=pk)
        if pro.product.seller == request.user:
            serializer=EditStatusSerializer(instance=pro,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'status':status.HTTP_200_OK,'msg':'status update'})
            else:
                return Response({'status':status.HTTP_404_NOT_FOUND,'msg':'enter the valid status'})
        else:
            return Response('you cannot edit other ordered status')
        
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
                    pro.product.quantity += pro.quantity
                    pro.product.save()
                    quantity=int(serializer.validated_data.get('quantity'))
                    amount=pro.product.price *quantity 
                    if quantity > 0:
                        if  pro.product.quantity >= quantity :
                            serializer.save(total_amount=amount)
                            pro.product.quantity -= quantity 
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
                    
class CancelOrderedView(GenericAPIView):
    permission_classes=[IsAuthenticated]
    
    def get_object(self, pk):
        try:
            return Buyproduct.objects.get(pk=pk)
        except Buyproduct.DoesNotExist:
            raise Http404
        
    def delete(self,request,pk):
        pro=self.get_object(pk=pk)
        if pro.user == request.user:
            pro.delete()
            return Response('your ordered cancel')
        else:
            return Response('you cannot cancel other user ordered')
        

class SearchView(ListAPIView):
    queryset=Product.objects.all()
    serializer_class=BuyerIndexSerializer
    filter_backends=[SearchFilter]
    search_fields=['^product_name']
    