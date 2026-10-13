# Euro Asia Homemade Foods

A mobile-friendly food ordering website built with Flask and Python for a small home-based food business. Customers can browse menus, place pre-orders and select available collection slots, while administrators can manage food events, menu items and customer orders.

## Features

### Customer Features

* Browse food menus organised by food events.
* View food descriptions and prices.
* Add items to a basket and adjust quantities.
* Place orders with customer details.
* Select an available collection time slot.
* Prevent selection of fully booked collection slots.
* View order confirmation after checkout.
* Access contact, privacy, terms and allergen information.

### Admin Features

* Secure admin login using password hashing.
* Create and manage food events.
* Set event dates, collection hours, slot durations and collection capacities.
* Automatically generate collection slots for food events.
* Add, edit and manage menu items.
* Configure menu item prices and available quantities.
* View and manage customer orders.
* Update order statuses, including New, Preparing, Ready, Collected and Cancelled.
* Track payment methods and payment statuses.

## Technologies Used

* **Backend:** Python, Flask
* **Database:** SQLite (development configuration), SQLAlchemy and Flask-SQLAlchemy
* **Forms and security:** Flask-WTF, CSRF protection and Werkzeug password hashing
* **Frontend:** HTML, CSS, Jinja2 templates
* **Configuration:** Python dotenv
* **Version control:** Git and GitHub

## Project Structure

```text
food-orders/
├── app.py
├── models.py
├── database.py
├── seed.py
├── requirements.txt
├── .env
├── templates/
│   ├── index.html
│   ├── basket.html
│   ├── checkout.html
│   ├── order_confirmation.html
│   └── ...
└── static/
    ├── style.css
    └── ...
```

*The structure above is illustrative. Update it to match the actual files in your repository. Do not commit your `.env` file.*

## Getting Started

### Prerequisites

* Python 3.10 or later
* pip
* Git

### 1. Clone the repository

```bash
git clone https://github.com/arifchou212/food-orders.git
cd food-orders
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
FLASK_SECRET_KEY=replace-with-a-long-random-secret
ADMIN_USERNAME=your-admin-username
ADMIN_PASSWORD=your-secure-admin-password
DATABASE_URL=sqlite:///food_orders.db
```

Generate a unique secret key and use a strong admin password. Never commit real credentials or production secrets to version control.

The application uses SQLite by default when `DATABASE_URL` is not set. Configure the database URL according to your chosen environment.

### 5. Initialise the database

The database setup depends on the current application configuration and whether migrations have been initialised.

If using the existing development setup, initialise the tables using the project's configured database setup. If Flask-Migrate is configured, apply the migrations with:

```bash
flask --app app db upgrade
```

Do not run both database initialisation methods indiscriminately against an existing database.

### 6. Run the application

```bash
python app.py
```

Open the local address displayed in the terminal, usually:

```text
http://127.0.0.1:5000
```

## Database Models

The application uses relational database models to represent:

* **FoodEvent:** Food events, dates and collection settings.
* **MenuItem:** Food descriptions, prices and available quantities.
* **CollectionSlot:** Collection times and booking capacities.
* **Customer:** Customer contact details.
* **Order:** Order totals, statuses, payment information and collection details.
* **OrderItem:** Ordered menu items, quantities and prices at the time of ordering.

SQLAlchemy manages database access and relationships between these models.

## Security Considerations

* Passwords should be stored as hashes rather than plaintext.
* CSRF protection is enabled for form submissions.
* Secret keys and administrator credentials should be stored in environment variables.
* Production deployments should use HTTPS and disable Flask debug mode.
* Customer information and database credentials must not be exposed in public repositories.
* Production databases should have a reliable backup and recovery process.

## Future Improvements

Potential future improvements include:

* Production deployment with persistent database storage.
* Automated database backups and recovery procedures.
* Automated order notifications.
* Improved reporting for food sales and order volumes.
* Further accessibility and mobile usability improvements.

## Author

**Arif Choudhury**

BSc (Hons) Software Engineering, First Class Honours
University of Leicester

GitHub: [arifchou212](https://github.com/arifchou212)

---

*Developed to support food pre-orders and collection management for a small food business.*
