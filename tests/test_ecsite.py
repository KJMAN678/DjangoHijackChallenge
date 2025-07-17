from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from ecsite.models import UserProfile, Product, Supply, PurchaseHistory


class ECSiteTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin_test',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            name='テスト管理者',
            is_admin=True
        )
        
        self.general_user = User.objects.create_user(
            username='user_test',
            password='user123'
        )
        self.general_profile = UserProfile.objects.create(
            user=self.general_user,
            name='テスト一般ユーザー',
            is_admin=False
        )
        
        self.product = Product.objects.create(
            name='テスト商品',
            price=Decimal('1000.00'),
            created_by=self.admin_user
        )
        
        self.supply = Supply.objects.create(
            product=self.product,
            quantity=10
        )
        
        self.client = Client()

    def test_product_list_view(self):
        """Test product list view displays products correctly"""
        response = self.client.get(reverse('ecsite:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テスト商品')
        self.assertContains(response, '¥1000.00')

    def test_product_create_admin_only(self):
        """Test that only admin users can create products"""
        self.client.login(username='admin_test', password='admin123')
        response = self.client.get(reverse('ecsite:product_create'))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(reverse('ecsite:product_create'), {
            'name': '新しい商品',
            'price': '2000.00'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        self.assertTrue(Product.objects.filter(name='新しい商品').exists())

    def test_product_create_general_user_denied(self):
        """Test that general users cannot create products"""
        self.client.login(username='user_test', password='user123')
        response = self.client.get(reverse('ecsite:product_create'))
        self.assertEqual(response.status_code, 302)  # Redirect to product list
        
        response = self.client.post(reverse('ecsite:product_create'), {
            'name': '一般ユーザー商品',
            'price': '1500.00'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(name='一般ユーザー商品').exists())

    def test_purchase_product_functionality(self):
        """Test product purchase functionality"""
        self.client.login(username='user_test', password='user123')
        
        response = self.client.get(reverse('ecsite:purchase_product', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テスト商品')
        
        response = self.client.post(reverse('ecsite:purchase_product', args=[self.product.id]), {
            'quantity': '2'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful purchase
        
        purchase = PurchaseHistory.objects.filter(
            purchased_by=self.general_user,
            product=self.product,
            quantity=2
        ).first()
        self.assertIsNotNone(purchase)

    def test_purchase_insufficient_stock(self):
        """Test purchase with insufficient stock"""
        self.client.login(username='user_test', password='user123')
        
        response = self.client.post(reverse('ecsite:purchase_product', args=[self.product.id]), {
            'quantity': '15'  # More than the 10 in stock
        })
        self.assertEqual(response.status_code, 200)  # Stay on same page with error
        
        purchase_count = PurchaseHistory.objects.filter(
            purchased_by=self.general_user,
            product=self.product
        ).count()
        self.assertEqual(purchase_count, 0)

    def test_purchase_history_view(self):
        """Test purchase history view"""
        PurchaseHistory.objects.create(
            product=self.product,
            quantity=3,
            purchased_by=self.general_user
        )
        
        self.client.login(username='user_test', password='user123')
        response = self.client.get(reverse('ecsite:purchase_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'テスト商品')
        self.assertContains(response, '3個')

    def test_user_profile_model(self):
        """Test UserProfile model functionality"""
        self.assertEqual(str(self.admin_profile), 'テスト管理者 (管理者)')
        self.assertEqual(str(self.general_profile), 'テスト一般ユーザー (一般ユーザー)')
        self.assertTrue(self.admin_profile.is_admin)
        self.assertFalse(self.general_profile.is_admin)

    def test_product_model(self):
        """Test Product model functionality"""
        self.assertEqual(str(self.product), 'テスト商品 (¥1000.00)')
        self.assertEqual(self.product.created_by, self.admin_user)

    def test_supply_model(self):
        """Test Supply model functionality"""
        self.assertEqual(str(self.supply), 'テスト商品 - 数量: 10')
        self.assertEqual(self.supply.product, self.product)

    def test_purchase_history_model(self):
        """Test PurchaseHistory model functionality"""
        purchase = PurchaseHistory.objects.create(
            product=self.product,
            quantity=5,
            purchased_by=self.general_user
        )
        self.assertEqual(str(purchase), 'user_test - テスト商品 x5')
        self.assertEqual(purchase.purchased_by, self.general_user)


class HijackFunctionalityTestCase(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='hijack_admin',
            password='admin123',
            is_staff=True,
            is_superuser=True
        )
        self.admin_profile = UserProfile.objects.create(
            user=self.admin_user,
            name='Hijack管理者',
            is_admin=True
        )
        
        self.target_user = User.objects.create_user(
            username='hijack_target',
            password='user123'
        )
        self.target_profile = UserProfile.objects.create(
            user=self.target_user,
            name='Hijackターゲット',
            is_admin=False
        )
        
        self.product = Product.objects.create(
            name='Hijackテスト商品',
            price=Decimal('500.00'),
            created_by=self.admin_user
        )
        
        Supply.objects.create(
            product=self.product,
            quantity=5
        )
        
        self.client = Client()

    def test_hijack_permission_admin_only(self):
        """Test that only admin users can access hijack functionality"""
        self.client.login(username='hijack_admin', password='admin123')
        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)

    def test_hijack_user_context(self):
        """Test that hijacked user context is properly handled"""
        
        self.client.login(username='hijack_admin', password='admin123')
        
        session = self.client.session
        session['hijack_history'] = [{
            'hijacker_id': self.admin_user.id,
            'hijacked_id': self.target_user.id
        }]
        session.save()
        
        self.client.force_login(self.target_user)
        
        response = self.client.get(reverse('ecsite:product_list'))
        self.assertEqual(response.status_code, 200)

    def test_hijacked_user_can_purchase(self):
        """Test that hijacked user can make purchases"""
        self.client.force_login(self.target_user)
        
        response = self.client.post(reverse('ecsite:purchase_product', args=[self.product.id]), {
            'quantity': '1'
        })
        self.assertEqual(response.status_code, 302)
        
        purchase = PurchaseHistory.objects.filter(
            purchased_by=self.target_user,
            product=self.product,
            quantity=1
        ).first()
        self.assertIsNotNone(purchase)

    def test_hijacked_user_cannot_create_products(self):
        """Test that hijacked general user still cannot create products"""
        self.client.force_login(self.target_user)
        
        response = self.client.get(reverse('ecsite:product_create'))
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        response = self.client.post(reverse('ecsite:product_create'), {
            'name': 'Hijack商品',
            'price': '1000.00'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(name='Hijack商品').exists())
