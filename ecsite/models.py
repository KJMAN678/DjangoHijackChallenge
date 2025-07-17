from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100, verbose_name='氏名')
    is_admin = models.BooleanField(default=False, verbose_name='管理ユーザーかいなか')
    
    class Meta:
        verbose_name = 'ユーザープロファイル'
        verbose_name_plural = 'ユーザープロファイル'
    
    def __str__(self):
        return f"{self.name} ({'管理者' if self.is_admin else '一般ユーザー'})"


class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name='商品名')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='単価')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='登録した管理ユーザーID')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日時')
    
    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
    
    def __str__(self):
        return f"{self.name} (¥{self.price})"


class Supply(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品ID')
    quantity = models.PositiveIntegerField(verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='登録日時')
    
    class Meta:
        verbose_name = '供給'
        verbose_name_plural = '供給'
    
    def __str__(self):
        return f"{self.product.name} - 数量: {self.quantity}"


class PurchaseHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='商品ID')
    quantity = models.PositiveIntegerField(verbose_name='購入数量')
    purchased_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='購入した一般ユーザーID')
    purchase_date = models.DateTimeField(default=timezone.now, verbose_name='購入日時')
    
    class Meta:
        verbose_name = '購入履歴'
        verbose_name_plural = '購入履歴'
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.purchased_by.username} - {self.product.name} x{self.quantity}"
