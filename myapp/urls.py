from django.urls import path
from .views import*

urlpatterns = [
    path('',index,name='index'),
    path('register/',CreateUserView.as_view()),
    path('login/',LoginUserView.as_view()),
    path('admin-index/',AdminIndexView.as_view()),
    path('verifay/<int:pk>',SellerVerificationView.as_view()),
    path('edit-profile/',EditUserView.as_view()),
    path('forgot-password/',ForgotPasswordView.as_view()),
    path('change-password/',UserChangePasswordview.as_view()),
    path('user-delete/<int:pk>',DeleteUserView.as_view()),
    
    
    path('seller-index/',SellerIndexView.as_view()),
    path('add-product/',AddProductView.as_view()),
    path('my-product/',ViewProductView.as_view()),
    path('edit-product/<int:pk>',EditProductView.as_view()),
    path('delete-product/<int:pk>',DeleteProductView.as_view()),
    path('edit-status/<int:pk>',EditStatusView.as_view()),
    
    path('buyer-index/',BuyerIndexView.as_view()),
    path('one-product/<int:pk>',OneProductView.as_view()),
    path('add-cart/<int:pk>',AddCartView.as_view()),
    path('my-cart/',MyCartView.as_view()),
    path('edit-cart/<int:pk>',EditCartView.as_view()),
    path('delete-cart/<int:pk>',DeleteCartView.as_view()),
    path('checkout/',CheckoutView.as_view()),
    path('buy-product/<int:pk>',BuyProductView.as_view()),
    path('my-buy/',MyBuyProductView.as_view()),
    path('edit-buyproduct/<int:pk>',EditMyBuyProductView.as_view()),
    path('cancel-orederd/<>int:pk>',CancelOrderedView.as_view()),
    path('search/',SearchView.as_view()),
    
    
]