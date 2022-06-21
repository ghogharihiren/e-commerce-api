from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
import datetime

# Create your models here.

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True
    
    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
class User(AbstractUser):
    role1=(('seller','Seller'),('buyer','Buyer'))
    email=models.EmailField(unique=True)
    mobile=models.CharField(max_length=15,null=True,blank=True)
    role=models.CharField(max_length=10,choices=role1)
    verification=models.BooleanField(default=False)
    
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()
    
    def __str__(self):
        return self.email

class Product(models.Model):
    cate=(
        ('fashion','Fashion'),
        ('electronic','Electronic'),
        ('home and kitchen','Home and kitchen'),
        ('travel','Travel'),
        ('toy','Toy'),
        ('beauty','Beauty'),
        ('food','Food'),
        ('stationery','stationery')
        
    )
    seller=models.ForeignKey(User,on_delete=models.CASCADE)
    product_name=models.CharField(max_length=100)
    category=models.CharField(max_length=100,choices=cate)    
    quantity=models.IntegerField()
    price=models.IntegerField()
    pic=models.FileField(upload_to='product/')
    description=models.TextField(max_length=200)
     
    def __str__(self):
        return self.category
    
    
class Mycart(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return self.user.email
        
    @property
    def total_cost(self):
        return self.quantity * self.product.price
    
class Buyproduct(models.Model):
    sta=(
        ('pending','Pending'),
        ('packing','Packing'),
        ('ready to dispatch','Ready to dispatch'),
        ('on the way','On the way'),
        ('ordered complate','Ordered complate'),
        
    )
    payment=(
        ('cash on delivery','cash on delivery'),
        ('online','Online'),
        
    )
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    addres=models.TextField(max_length=500)
    status=models.CharField(max_length=100,choices=sta,default='pending')
    payment_method=models.CharField(max_length=50,choices=payment)
    total_amount=models.PositiveIntegerField()
    ordered_date=models.DateField(default=datetime.date.today)
    quantity=models.PositiveIntegerField(default=1)
    
    
    def _str__(self):
        return self.user.email
    