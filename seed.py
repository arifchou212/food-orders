from datetime import date

from app import app
from models import db, FoodEvent, MenuItem


with app.app_context():

    event = FoodEvent(
        name="Saturday Food",
        event_date=date(2026, 9, 19),
        active=True
    )

    db.session.add(event)

    db.session.flush()


    biryani = MenuItem(
        event_id=event.id,
        name="Chicken Biryani",
        description="Fragrant basmati rice with chicken and spices.",
        price=8.00,
        production_quantity=40,
        remaining_quantity=40,
        active=True
    )


    samosa = MenuItem(
        event_id=event.id,
        name="Samosa",
        description="Crispy homemade samosas.",
        price=2.00,
        production_quantity=60,
        remaining_quantity=60,
        active=True
    )


    db.session.add_all([
        biryani,
        samosa
    ])


    db.session.commit()


    print("Food event and menu created.")