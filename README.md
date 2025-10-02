# 🛒 E-Commerce Platform (Django + PostgreSQL + Celery + RabbitMQ + Redis + Stripe)

## Overview
A production-ready e-commerce web application built with **Django** and styled with **Bootstrap**.  
This repository implements a modular architecture (accounts, products, cart, orders, payments, coupons, webshop), integrates **Stripe** for payments, uses **PostgreSQL** as the primary data store, and relies on **Celery + RabbitMQ** for background processing and **Redis** for analytics / activity tracking and recommendation features.

> Note: earlier documentation mistakenly referenced SQLite — this project uses **PostgreSQL** as the canonical database.  

---

## Key features
- User accounts: registration, login, profile management  
- Product catalog: categories, product pages, search & filters  
- Shopping cart and checkout flow  
- Orders management and history  
- Stripe integration with webhook handling for payments  
- Coupons and discount system  
- Admin panel (Django Admin) for full CRUD of products, orders, users, coupons  
- Background jobs (emails, order processing, analytics) via Celery + RabbitMQ  
- Redis for session/cache and user activity tracking to enable product recommendations  
- HTTPS-ready (certificates included in repo for development / testing)

---

## Technology stack
- **Backend:** Python, Django  
- **Database:** PostgreSQL  
- **Task queue / broker:** Celery + RabbitMQ  
- **Cache / activity store:** Redis  
- **Payments:** Stripe API (webhooks)  
- **Frontend:** Bootstrap, HTML, CSS  
- **Containerized services (recommended for dev):** Docker (RabbitMQ, Redis, optional Postgres container)  

---

## Prerequisites
- Python 3.10+  
- pip  
- PostgreSQL server (local or remote)  
- Docker (for RabbitMQ / Redis in development)  
- Stripe CLI (for local webhook testing)  
- (Optional) virtualenv / venv

---

## Environment variables (example `.env`)
```env
# Django
SECRET_KEY=change_this_to_a_strong_value
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (PostgreSQL)
DATABASE_URL=postgresql://ecommerce_user:strongpassword@localhost:5432/e_commerce

# Celery / Broker
CELERY_BROKER_URL=amqp://guest:guest@localhost:5672//

# Redis
REDIS_URL=redis://localhost:6379/0

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```
- 1. Local development — quickstart

Clone the repo
```bash
git clone https://github.com/ArutyunyanA/e_commerce.git
cd e_commerce
```
- 2. Create virtualenv and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate       # macOS / Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```
- 3. Prepare PostgreSQL
Create database and user (example using psql as the postgres superuser):

```sql
-- inside psql (psql -U postgres)
CREATE DATABASE e_commerce;
CREATE USER ecommerce_user WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE e_commerce TO ecommerce_user;
\q
```

```bash
psql -U postgres -c "CREATE DATABASE e_commerce;"
psql -U postgres -c "CREATE USER ecommerce_user WITH PASSWORD 'strongpassword';"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE e_commerce TO ecommerce_user;"
```
Make sure DATABASE_URL in .env points to the created DB.

- 4. Run Django migrations

```bash
python3 manage.py migrate
```
- 5. (Optional) Create superuser

```bash
python3 manage.py createsuperuser
```

- 6. Start required services (RabbitMQ, Redis)
Run these in separate terminals (or use Docker Compose):

```bash
python manage.py runserver
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management
docker run -it --rm --name redis -p 6379:6379 redis
celery -A e_commerce worker -l info
stripe listen --forward-to localhost:8000/payment/webhook/
```
