from datetime import date, datetime, timedelta

from app import app
from models import db, FoodEvent, MenuItem, CollectionSlot


with app.app_context():

    # Clear existing test data
    db.drop_all()
    db.create_all()

    # -----------------------------
    # Food event
    # -----------------------------

    event_date = date(2026, 10, 10)

    collection_start_time = datetime.strptime(
        "12:00",
        "%H:%M"
    ).time()

    collection_end_time = datetime.strptime(
        "14:00",
        "%H:%M"
    ).time()

    collection_slot_duration = 30
    collection_slot_capacity = 2

    event = FoodEvent(
        name="Saturday Food",
        event_date=event_date,
        collection_start_time=collection_start_time,
        collection_end_time=collection_end_time,
        collection_slot_duration=collection_slot_duration,
        collection_slot_capacity=collection_slot_capacity,
        active=True
    )

    db.session.add(event)
    db.session.flush()


    # -----------------------------
    # Generate collection slots
    # -----------------------------

    current_start = collection_start_time

    while current_start < collection_end_time:

        current_start_datetime = datetime.combine(
            event_date,
            current_start
        )

        current_end_datetime = (
            current_start_datetime
            + timedelta(minutes=collection_slot_duration)
        )

        current_end = current_end_datetime.time()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=current_start,
            end_time=current_end,
            capacity=collection_slot_capacity
        )

        db.session.add(slot)

        current_start = current_end


    # -----------------------------
    # Menu
    # -----------------------------

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


    print("Test database created.")
    print()
    print("Event:")
    print(f"  {event.name}")
    print(f"  {event.event_date}")
    print()
    print("Collection:")
    print("  12:00 - 14:00")
    print("  30 minute slots")
    print("  2 orders per slot")
    print()
    print("Slots:")
    
    for slot in event.collection_slots:
        print(
            f"  {slot.start_time.strftime('%H:%M')} - "
            f"{slot.end_time.strftime('%H:%M')} "
            f"(capacity {slot.capacity})"
        )