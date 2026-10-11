from django.contrib.auth import get_user_model
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        # метод get_user_model() возвращает кастомную модель пользователя, которая указана
        # в настройках AUTH_USER_MODEL в config/settings.py
        User = get_user_model() #  получаем саму модель пользователя
        user = User.objects.create(
            email='testadmin@sky.pro',
            first_name='Admin',
            last_name='Admin',
        )                               #  создаем конкретный экземпляр модели пользователя

        user.set_password('1234') # метод используется для хеширования пароля перед его сохранением.

        user.is_staff=True
        user.is_superuser=True

        user.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully created admin user with email {user.email}!'))

# более подходящий вариант, но не сработает, тк.  кастомный UserManager в проекте не переопределяет
# метод create_superuser — используется стандартный менеджер Django, который обязательно требует username первым
# позиционным аргументом.
# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         User = get_user_model()
#         user = User.objects.create_superuser(
#             email='testadmin@sky.pro',
#             password='1234',
#             first_name='Admin',
#             last_name='Admin',
#         )
#
#         user.save()
#
#         self.stdout.write(self.style.SUCCESS(f'Successfully created admin user with email {user.email}!'))

# метод create_superuser() не только хэширует пароль, но и автоматически устанавливает поля is_staff и is_superuser
# в True, а также автоматически сохраняет объект в базу данных сразу при вызове