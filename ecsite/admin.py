from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Product, Supply, PurchaseHistory


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'ユーザープロファイル'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'created_by', 'created_at')
    list_filter = ('created_by', 'created_at')
    search_fields = ('name',)
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Supply)
class SupplyAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'created_at')
    list_filter = ('product', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(PurchaseHistory)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    list_display = ('purchased_by', 'product', 'quantity', 'purchase_date')
    list_filter = ('product', 'purchase_date', 'purchased_by')
    readonly_fields = ('purchase_date',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.purchased_by = request.user
        super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
