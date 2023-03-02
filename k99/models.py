from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
import datetime

class CustomerManager(BaseUserManager):
    def create_customer(self, username, kname, kid, doe, sigungu, dong, sangse, sname, note, zipcode, cdate, edate, regular, cphone, email, password=None):
        # if not email:
        #     raise ValueError(_('Users must have an email address'))
        # not null 변수들 처리?
        customer = Customer(
            username=username,
            password=password,
            real_pw=password,
            kname=kname,
            kid=kid,
            doe=doe,
            sigungu=sigungu,
            dong=dong,
            sangse=sangse,
            sname=sname,
            note=note,
            zipcode=zipcode,
            cdate=cdate,
            edate=edate,
            regular=regular,
            cphone=cphone,
            email=email,
            #email=self.normalize_email(email),
        )

        customer.is_staff = False
        customer.is_superuser = False
        customer.is_active = True
        customer.date_joined = datetime.datetime.now()
        customer.last_login = datetime.datetime.now()
        customer.set_password(password)
        customer.save(using=self._db)
        return customer

    def create_superuser(self, email, username, password):
        customer = self.create_customer(
            email=email,
            password=password,
            username=username
        )
        customer.is_superuser = True
        customer.save(using=self._db)

        return customer


class Customer(AbstractUser):
    kid = models.AutoField(unique=True, primary_key=True)
    kname = models.CharField(max_length=200, null = True, blank= True)
    doe = models.CharField(max_length=500, null = True, blank= True)
    sigungu = models.CharField(max_length=500, null = True, blank= True)
    dong = models.CharField(max_length=500, null = True, blank= True)
    sangse = models.CharField(max_length=500, null = True, blank= True)
    sname = models.CharField(max_length=50, null = True, blank= True)
    note = models.CharField(max_length=500, null = True, blank= True)
    cphone = models.CharField(max_length=500, null = True, blank= True)
    zipcode = models.CharField(max_length=5, null = True, blank = True)
    cdate = models.DateTimeField(null=True, blank = True)
    edate = models.DateTimeField(null=True, blank=True)
    regular = models.BooleanField(null=True)
    residual = models.IntegerField(null=True)
    real_pw = models.TextField(null=True)
    first_name = None
    last_name = None

    def __str__(self):
        return self.kname

class Product(models.Model):
    pid = models.IntegerField(unique=True, primary_key = True)
    pname = models.CharField(max_length=50, null = True, blank= True)
    pprice = models.IntegerField()

    def __str__(self):
        return self.pname

class Buy(models.Model):
    bid = models.IntegerField(unique=True, primary_key = True)
    bamount = models.IntegerField(default=5, null = True, blank= True)
    bdate = models.DateField(null = True, blank= True)
    kid = models.ForeignKey(Customer, on_delete=models.CASCADE)
    pid = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return self.bid

class Posts(models.Model):
    pid = models.IntegerField(unique=True, primary_key=True)
    kid = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, null=True)
    create_date = models.DateTimeField(null=True)
    content = models.TextField(null=True)
    tag = models.TextField(null=True)
    pvurl = models.TextField(null=True)

class Realexamples(models.Model):
    pid = models.ForeignKey(Posts, on_delete=models.DO_NOTHING)
    material_out = models.TextField(null=True)
    material_in = models.TextField(null=True)
    issue = models.TextField(null=True)
    issue_detail = models.TextField(null=True)
    color = models.CharField(max_length=5, null=True)
    comb_colors = models.BooleanField(null=True)
    printing = models.BooleanField(null=True)
    clothes = models.TextField(null=True)
    luxury = models.BooleanField(null=True)
    mix = models.BooleanField(null=True)
    mix_white = models.BooleanField(null=True)

class QnA(models.Model):
    pid = models.ForeignKey(Posts, on_delete=models.DO_NOTHING)
    category = models.TextField(null=True)
    subject = models.TextField(null=True)
    prof = models.BooleanField(null=True)

class Searchlog(models.Model):
    sid = models.AutoField(unique=True, primary_key=True)
    kid = models.IntegerField(null=True)
    date = models.DateTimeField(null=True, blank=True)
    mix = models.BooleanField(null=True)
    mix_white = models.BooleanField(null=True)
    clothes = models.TextField(null=True)
    material = models.TextField(null=True)
    color = models.TextField(null=True)
    # comb_colors = models.BooleanField(null=True)
    # printing = models.BooleanField(null=True)
    issue = models.TextField(null=True)
    issue_detail = models.TextField(null=True)
    luxury = models.BooleanField(null=True)
    stage = models.TextField(null=True)
    finish = models.BooleanField(null=True, default=False)
