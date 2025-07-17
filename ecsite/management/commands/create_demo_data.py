from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ecsite.models import UserProfile, Product, Supply, PurchaseHistory
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create demo data for ECsite with hijack functionality'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo data...')

        admin_user, created = User.objects.get_or_create(
            username='admin_user',
            defaults={
                'email': 'admin@example.com',
                'first_name': '管理者',
                'last_name': '太郎',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')

        admin_profile, created = UserProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'name': '管理者 太郎',
                'is_admin': True,
            }
        )
        if created:
            self.stdout.write(f'Created admin profile: {admin_profile.name}')

        general_users = [
            ('user1', '一般ユーザー 花子', 'user1@example.com'),
            ('user2', '一般ユーザー 次郎', 'user2@example.com'),
            ('user3', '一般ユーザー 三郎', 'user3@example.com'),
        ]

        for username, name, email in general_users:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': name.split()[1],
                    'last_name': name.split()[0],
                }
            )
            if created:
                user.set_password('user123')
                user.save()
                self.stdout.write(f'Created general user: {user.username}')

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'name': name,
                    'is_admin': False,
                }
            )
            if created:
                self.stdout.write(f'Created user profile: {profile.name}')

        products_data = [
            ('ノートパソコン', Decimal('89800.00')),
            ('ワイヤレスマウス', Decimal('2980.00')),
            ('キーボード', Decimal('5500.00')),
            ('モニター', Decimal('25800.00')),
            ('スマートフォン', Decimal('78000.00')),
            ('タブレット', Decimal('45000.00')),
        ]

        for product_name, price in products_data:
            product, created = Product.objects.get_or_create(
                name=product_name,
                defaults={
                    'price': price,
                    'created_by': admin_user,
                }
            )
            if created:
                self.stdout.write(f'Created product: {product.name} (¥{product.price})')

        products = Product.objects.all()
        supply_quantities = [50, 100, 75, 30, 25, 40]

        for product, quantity in zip(products, supply_quantities):
            supply, created = Supply.objects.get_or_create(
                product=product,
                defaults={'quantity': quantity}
            )
            if created:
                self.stdout.write(f'Created supply: {product.name} - {quantity} units')

        user1 = User.objects.get(username='user1')
        user2 = User.objects.get(username='user2')

        purchase_data = [
            (user1, products[0], 1),  # user1 buys laptop
            (user1, products[1], 2),  # user1 buys 2 mice
            (user2, products[2], 1),  # user2 buys keyboard
            (user2, products[3], 1),  # user2 buys monitor
        ]

        for user, product, quantity in purchase_data:
            purchase, created = PurchaseHistory.objects.get_or_create(
                purchased_by=user,
                product=product,
                quantity=quantity,
                defaults={'quantity': quantity}
            )
            if created:
                self.stdout.write(f'Created purchase: {user.username} bought {quantity}x {product.name}')

        self.stdout.write(
            self.style.SUCCESS('Demo data created successfully!')
        )
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('Admin user: admin_user / admin123')
        self.stdout.write('General users: user1, user2, user3 / user123')
        self.stdout.write('')
        self.stdout.write('You can now test hijack functionality:')
        self.stdout.write('1. Login as admin_user in /admin/')
        self.stdout.write('2. Go to Users section and hijack user1, user2, or user3')
        self.stdout.write('3. Navigate to / to see the EC site as the hijacked user')
        self.stdout.write('4. Try purchasing products as the hijacked user')
