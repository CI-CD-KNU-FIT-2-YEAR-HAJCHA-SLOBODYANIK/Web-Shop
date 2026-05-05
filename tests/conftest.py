import os
import django

# Встановлюємо налаштування та ініціалізуємо Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
