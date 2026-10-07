# TravelPay AI — Railway Deploy-Ready

TravelPay AI is a hackathon prototype for AI-assisted travel payments. This package is prepared to run as **one public web application** from a single Railway service, with Railway MySQL as the database.

## Production architecture

- Flask + Gunicorn serves the frontend and `/api/*` from the same domain.
- Railway MySQL stores traveler profiles, budgets and simulated transactions.
- Frontend API calls use relative `/api` paths — there are no hard-coded `localhost` or `127.0.0.1` API URLs.
- Optional Serper and Google Places keys remain server-side.
- `/health` is provided for Railway health checks.

## Deploy to Railway

1. Put this project in a GitHub repository.
2. In Railway, create a new project and deploy the GitHub repository.
3. Add a **MySQL** service to the same Railway project.
4. The application automatically understands Railway's native MySQL variables: `MYSQLHOST`, `MYSQLPORT`, `MYSQLUSER`, `MYSQLPASSWORD`, and `MYSQLDATABASE`.
5. Run `database/schema.sql` against the Railway MySQL database once.
6. Optional: add `SERPER_API_KEY` and/or `GOOGLE_PLACES_API_KEY` as Railway service variables to enable live price evidence.
7. Deploy. Railway starts the app with:

```text
gunicorn --chdir backend app:app
```

8. In Railway, open the service's **Networking** settings and generate a public domain. That URL is the single public URL for login, dashboard, QR Pay, Live Prices, Voice AI, payment review and APIs.

## Local development

```cmd
cd TravelPay-AI-New\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python app.py
```

Then open `http://127.0.0.1:5000/`.

For local MySQL, set the `MYSQL_*` variables in `backend/.env` and run `database/schema.sql` against your local database.

## Public HTTPS features

Camera scanning and browser voice features work best on the Railway HTTPS domain. Browser permissions may still vary by device/browser.

## Important hackathon limitation

The payment button records a **simulated transaction** in MySQL. It does not connect to a bank, UPI payment gateway, or real-money transfer system.

## Live price intelligence

The project deliberately does not use a fake `local_prices` dataset. If fewer than two usable exact INR price observations are found, the app says there is not enough verified evidence rather than inventing an average.
