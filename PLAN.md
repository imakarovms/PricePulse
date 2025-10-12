### **День 1: Настройка проекта и окружения**
- [x] Создать репозиторий на GitHub
- [x] Инициализировать Django проект (`django-admin startproject pricepulse`)
- [x] Настроить виртуальное окружение и `requirements.txt`
- [x] Добавить `.gitignore` (Python, Django, IDE)
- [x] Установить: `djangorestframework`, `djangorestframework-simplejwt`, `psycopg2`, `python-decouple`
- [x] Настроить `settings.py`: разделение на `base.py`, `local.py`, `prod.py` (опционально, но круто)
- **Результат**: Чистый Django-проект, запускается `runserver`

### **День 2: Docker и PostgreSQL**
- [x] Написать `Dockerfile` для Django
- [x] Создать `docker-compose.yml` с:
  - `db` (PostgreSQL)
  - `web` (Django)
- [x] Настроить подключение Django к PostgreSQL в контейнере
- [x] Протестировать: `docker-compose up --build` → миграции → сайт работает
- **Результат**: Проект запускается в Docker, использует PostgreSQL

### **День 3: Аутентификация (JWT)**
- [ ] Установить `djangorestframework-simplejwt`
- [ ] Создать приложение `users`
- [ ] Реализовать:
  - `User` модель (стандартная)
  - `RegisterView`
  - `TokenObtainPairView` (из simplejwt)
- [ ] Настроить маршруты: `/api/auth/register/`, `/api/auth/login/`
- [ ] Протестировать в Postman/Swagger: регистрация → получение токена
- **Результат**: Пользователь может зарегистрироваться и залогиниться

---

### **День 4: Модель TrackedProduct + DRF API (CRUD)**
- [ ] Создать приложение `tracker`
- [ ] Модель `TrackedProduct`:
  ```python
  user = ForeignKey(User)
  url = URLField()
  title = CharField(max_length=300)
  brand = CharField(max_length=100, blank=True)
  current_price = DecimalField(max_digits=10, decimal_places=2)
  is_in_stock = BooleanField(default=True)
  created_at = DateTimeField(auto_now_add=True)
  price_history = JSONField(default=list)
  ```
- [ ] Создать `TrackedProductSerializer`
- [ ] Реализовать `TrackedProductViewSet` (ModelViewSet)
- [ ] Настроить маршруты: `/api/tracked-products/`
- **Результат**: Можно создавать/читать товары через API (пока без парсинга)

---

### **День 5: Первый парсер — Ozon (без Selenium!)**
- [ ] Проанализировать страницу Ozon через DevTools:
  - Найти структуру цены, названия
  - Проверить наличие JSON-LD
- [ ] Написать `parsers/ozon.py`:
  ```python
  def parse_ozon(url: str) -> dict:
      # requests + BeautifulSoup
      # Возвращает {"title": "...", "price": 94990.00, "brand": "Apple", "in_stock": True}
  ```
- [ ] Добавить валидацию URL (только `ozon.ru/product/`)
- [ ] Протестировать парсер отдельно (через `python -c "..."`)
- **Результат**: Функция `parse_ozon()` возвращает данные по URL

---

### **День 6: Интеграция парсера в API**
- [ ] В `TrackedProductViewSet.create()`:
  - Вызвать парсер после сохранения URL
  - Обновить поля `title`, `current_price` и т.д.
  - Добавить первую запись в `price_history`
- [ ] Обработка ошибок: если парсинг упал — возвращать 400 с ошибкой
- [ ] Протестировать: отправка URL Ozon → в ответе полные данные
- **Результат**: При добавлении ссылки Ozon — автоматически заполняются данные

---

### **День 7: Поддержка Wildberries + DNS**
- [ ] Аналогично Ozon: написать `parsers/wildberries.py`, `parsers/dns.py`
- [ ] Создать фабрику парсеров:
  ```python
  def get_parser(url: str):
      if "ozon.ru" in url: return parse_ozon
      if "wildberries.ru" in url: return parse_wildberries
      if "dns-shop.ru" in url: return parse_dns
      raise ValueError("Unsupported store")
  ```
- [ ] Обновить `create()` в ViewSet: использовать фабрику
- **Результат**: Поддержка 3 магазинов в одном эндпоинте

---

## 📅 Неделя 2: Celery, Redis, Кэш

### **День 8: Настройка Redis**
- [ ] Добавить сервис `redis` в `docker-compose.yml`
- [ ] Установить `redis` и `django-redis`
- [ ] Настроить кэширование в `settings.py`:
  ```python
  CACHES = {
      "default": {
          "BACKEND": "django.core.cache.backends.redis.RedisCache",
          "LOCATION": "redis://redis:6379/1",
      }
  }
  ```
- [ ] Протестировать: `cache.set("test", "ok")` → `cache.get("test")`
- **Результат**: Redis работает как кэш

---

### **День 9: Celery + Redis как брокер**
- [ ] Установить `celery[redis]`
- [ ] Создать `celery.py` в корне проекта
- [ ] Настроить:
  ```python
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricepulse.settings')
  app = Celery('pricepulse')
  app.config_from_object('django.conf:settings', namespace='CELERY')
  app.autodiscover_tasks()
  ```
- [ ] В `settings.py`:
  ```python
  CELERY_BROKER_URL = "redis://redis:6379/0"
  CELERY_RESULT_BACKEND = "redis://redis:6379/0"
  ```
- [ ] Добавить `celery` в `docker-compose.yml` (worker)
- **Результат**: Celery подключён к Redis

---

### **День 10: Первая Celery-задача — обновление цены**
- [ ] В `tracker/tasks.py`:
  ```python
  @shared_task
  def update_product_price(product_id):
      product = TrackedProduct.objects.get(id=product_id)
      parser = get_parser(product.url)
      data = parser(product.url)
      # Обновить product, добавить в историю
      product.save()
  ```
- [ ] Протестировать: вызвать задачу вручную через shell
- **Результат**: Фоновая задача обновляет цену

---

### **День 11: Кэширование HTML в парсерах**
- [ ] В каждом парсере:
  ```python
  from django.core.cache import cache
  cache_key = f"html:{url}"
  html = cache.get(cache_key)
  if not html:
      html = requests.get(url).text
      cache.set(cache_key, html, timeout=3600)  # 1 час
  ```
- [ ] Обработка исключений (таймаут, 403, 500)
- **Результат**: Один и тот же URL не парсится чаще 1 раза в час

---

### **День 12: История цен**
- [ ] В `update_product_price`: добавлять новую запись в `price_history`
- [ ] Создать эндпоинт `PriceHistoryView` (APIView)
- [ ] Протестировать: несколько обновлений → история растёт
- **Результат**: Можно получить историю цен по товару

---

### **День 13: Уведомления (Email)**
- [ ] Настроить email в `settings.py` (использовать `console.EmailBackend` для dev)
- [ ] В `notifications/services.py`:
  ```python
  def send_price_drop_alert(user, product, old_price, new_price):
      # send_mail(...)
  ```
- [ ] Вызывать в `update_product_price`, если `new_price < old_price`
- **Результат**: При падении цены — письмо в консоль (в продакшене — на почту)

---

### **День 14: Celery Beat — автоматическая проверка**
- [ ] В `settings.py`:
  ```python
  from celery.schedules import crontab
  CELERY_BEAT_SCHEDULE = {
      'check-all-prices': {
          'task': 'tracker.tasks.check_all_prices',
          'schedule': crontab(minute=0, hour='*/6'),  # каждые 6 часов
      },
  }
  ```
- [ ] Написать задачу `check_all_prices`:
  ```python
  @shared_task
  def check_all_prices():
      for product in TrackedProduct.objects.all():
          update_product_price.delay(product.id)
  ```
- [ ] Добавить `beat` в `docker-compose.yml`
- **Результат**: Каждые 6 часов все товары проверяются автоматически

---

## 📅 Неделя 3: Тесты, Документация, Доработки

### **День 15–16: Тесты для парсеров**
- [ ] Написать `test_parsers.py`:
  - Мокать `requests.get`
  - Проверять корректность извлечения цены/названия
- [ ] Использовать `pytest` + `responses` или `unittest.mock`
- **Результат**: Парсеры покрыты unit-тестами

---

### **День 17–18: Тесты для API и задач**
- [ ] Тесты для `TrackedProductViewSet` (создание, чтение)
- [ ] Тесты для `update_product_price` (с моком парсера)
- [ ] Проверка, что задача вызывается при создании товара
- **Результат**: Основная логика покрыта тестами (70%+)

---

### **День 19: OpenAPI документация**
- [ ] Установить `drf-spectacular`
- [ ] Настроить в `settings.py`
- [ ] Добавить `SpectacularAPIView`, `SwaggerUI`
- [ ] Протестировать: `/api/schema/swagger-ui/`
- **Результат**: Автоматическая документация API

---

### **День 20: README.md**
- [ ] Описание проекта
- [ ] Схема архитектуры (текстовая)
- [ ] Инструкция по запуску:
  ```bash
  git clone ...
  docker-compose up --build
  ```
- [ ] Примеры запросов (curl или Postman)
- [ ] Скриншоты: Swagger, история цен
- **Результат**: Полноценный README для GitHub

---

### **День 21: Оптимизация и обработка ошибок**
- [ ] Добавить rate limiting на `/api/tracked-products/`
- [ ] Обработка 403/429 от магазинов (повтор с экспоненциальной задержкой)
- [ ] Логирование ошибок парсинга
- **Результат**: Система устойчива к сбоям

---

## 📅 Неделя 4: Демо, Финальная сборка, Портфолио

### **День 22–23: Демо-видео (2 минуты)**
1. Регистрация
2. Добавление ссылки Ozon
3. Показ истории цен
4. Имитация падения цены → показ email-уведомления в консоли
5. Просмотр списка товаров
- **Результат**: Короткое видео для README или LinkedIn

---

### **День 24: Поддержка Citilink и М.Видео**
- [ ] Дописать парсеры для 2 дополнительных магазинов
- [ ] Протестировать все 5 магазинов
- **Результат**: Поддержка 5 магазинов

---

### **День 25: Финальное тестирование**
- [ ] Прогон всех тестов
- [ ] Проверка запуска через Docker
- [ ] Проверка Celery Beat (вручную запустить задачу)
- **Результат**: Система стабильно работает

---

### **День 26: Очистка кода**
- [ ] Удалить дубли
- [ ] Добавить типизацию (опционально)
- [ ] Проверить PEP8
- **Результат**: Чистый, читаемый код

---

### **День 27: Подготовка к собеседованию**
- [ ] Написать краткое описание проекта (3 предложения)
- [ ] Выделить ключевые технологии: Django, DRF, Celery, Redis, Docker
- [ ] Подготовить ответы на вопросы:
  - «Почему не Selenium?»
  - «Как вы обрабатываете ошибки парсинга?»
  - «Как масштабировать систему?»

---

### **День 28–30: Резерв / Улучшения**
- [ ] Добавить пагинацию
- [ ] Реализовать удаление товара
- [ ] Добавить фильтрацию по бренду/цене
- [ ] Или: начать Telegram-бота (опционально)

---

## ✅ Финальный результат (на день 30):

- **Рабочий проект** в GitHub с Docker
- **5 магазинов** в парсерах
- **Celery + Redis** для фоновых задач и кэша
- **Email-уведомления** при снижении цены
- **История цен** и API
- **Тесты**, **документация**, **README**, **демо-видео**
