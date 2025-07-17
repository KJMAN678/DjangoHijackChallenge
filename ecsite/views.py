from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from .models import Product, Supply, PurchaseHistory, UserProfile


def product_list(request):
    products = Product.objects.all()
    
    for product in products:
        total_supply = Supply.objects.filter(product=product).aggregate(
            total=Sum('quantity'))['total'] or 0
        total_purchased = PurchaseHistory.objects.filter(product=product).aggregate(
            total=Sum('quantity'))['total'] or 0
        product.available_quantity = total_supply - total_purchased
    
    return render(request, 'ecsite/product_list.html', {'products': products})


@login_required
def product_create(request):
    try:
        profile = request.user.profile
        if not profile.is_admin:
            messages.error(request, '管理ユーザーのみ商品を登録できます。')
            return redirect('ecsite:product_list')
    except UserProfile.DoesNotExist:
        messages.error(request, 'ユーザープロファイルが設定されていません。')
        return redirect('ecsite:product_list')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        
        if name and price:
            try:
                product = Product.objects.create(
                    name=name,
                    price=float(price),
                    created_by=request.user
                )
                messages.success(request, f'商品「{product.name}」を登録しました。')
                return redirect('ecsite:product_list')
            except ValueError:
                messages.error(request, '価格は数値で入力してください。')
        else:
            messages.error(request, '商品名と価格を入力してください。')
    
    return render(request, 'ecsite/product_create.html')


@login_required
def purchase_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    total_supply = Supply.objects.filter(product=product).aggregate(
        total=Sum('quantity'))['total'] or 0
    total_purchased = PurchaseHistory.objects.filter(product=product).aggregate(
        total=Sum('quantity'))['total'] or 0
    available_quantity = total_supply - total_purchased
    
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        
        if quantity:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    messages.error(request, '購入数量は1以上で入力してください。')
                elif quantity > available_quantity:
                    messages.error(request, f'在庫が不足しています。利用可能数量: {available_quantity}')
                else:
                    PurchaseHistory.objects.create(
                        product=product,
                        quantity=quantity,
                        purchased_by=request.user
                    )
                    messages.success(request, f'「{product.name}」を{quantity}個購入しました。')
                    return redirect('ecsite:product_list')
            except ValueError:
                messages.error(request, '購入数量は数値で入力してください。')
        else:
            messages.error(request, '購入数量を入力してください。')
    
    context = {
        'product': product,
        'available_quantity': available_quantity,
    }
    return render(request, 'ecsite/purchase_product.html', context)


@login_required
def purchase_history(request):
    history = PurchaseHistory.objects.filter(purchased_by=request.user).order_by('-purchase_date')
    
    for item in history:
        item.total_price = item.product.price * item.quantity
    
    return render(request, 'ecsite/purchase_history.html', {'history': history})
