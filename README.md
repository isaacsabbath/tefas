#        Tefas Pharmacy

Django e-commerce site for over-the-counter pharmacy products with M-Pesa checkout, delivery or pickup, and Django admin product/order management.

## Setup

1. Create and activate the local environment:

```bash
virtualenv .venv
. .venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install Tailwind build dependencies and compile the stylesheet:

```bash
cd theme/static_src
npm install
cd ../..
.venv/bin/python manage.py tailwind build
```

4. Copy `.env.example` to `.env` and fill in the values.

5. Run migrations and seed data:

```bash
.venv/bin/python manage.py migrate
.venv/bin/python manage.py seed_demo_data
```

6. Start the server:

```bash
.venv/bin/python manage.py runserver
```

## M-Pesa sandbox

Use the Safaricom Daraja sandbox and set these values in `.env`:

- `MPESA_CONSUMER_KEY`
- `MPESA_CONSUMER_SECRET`
- `MPESA_SHORTCODE`
- `MPESA_PASSKEY`
- `MPESA_CALLBACK_URL`

Expose the callback locally with a tunnel such as ngrok and point `MPESA_CALLBACK_URL` to `/payments/mpesa/callback/`.

## Admin

Log in at `/admin/` with a superuser account. Products, categories, pickup locations, and orders are all managed from Django admin.

## Tests

Run the test suite with:

```bash
.venv/bin/python manage.py test
```