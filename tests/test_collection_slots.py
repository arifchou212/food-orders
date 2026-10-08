from datetime import date, time

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest

from app import app
from models import (
    db,
    FoodEvent,
    CollectionSlot,
    MenuItem,
    Order,
    OrderItem,
    Customer
)
@pytest.fixture
def client():

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():

        db.drop_all()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()
        
def test_collection_slot_capacity(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)

        db.session.commit()
        
        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }
        
        response = client.post(
            "/checkout",
            data={
                "name": "Customer One",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )
        
        assert response.status_code == 200, response.location
        assert Order.query.count() == 1
        
        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Customer Two",
                "phone": "07987654321",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert Order.query.count() == 2
        
        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Customer Three",
                "phone": "07876543210",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"slot is now full" in response.data
        assert Order.query.count() == 2
        
def test_cancelled_order_does_not_use_slot_capacity(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        db.session.commit()
        
        customer = Customer(
            name="Test Customer",
            phone="07123456789"
        )

        db.session.add(customer)
        db.session.flush()

        cancelled_order = Order(
            event_id=event.id,
            customer_id=customer.id,
            total=10.00,
            status="Cancelled",
            fulfilment_method="Collection",
            collection_slot_id=slot.id
        )

        db.session.add(cancelled_order)
        db.session.commit()
        
        active_order_count = Order.query.filter_by(
            collection_slot_id=slot.id
        ).filter(
            Order.status != "Cancelled"
        ).count()

        assert active_order_count == 0
        assert active_order_count < slot.capacity
        
def test_checkout_requires_name(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Please enter your name and phone number." in response.data
        assert Order.query.count() == 0
        
def test_checkout_rejects_invalid_phone(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "123",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Please enter a valid phone number." in response.data
        assert Order.query.count() == 0
        
def test_checkout_requires_collection_slot(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": ""
            }
        )

        assert response.status_code == 200
        assert b"Please choose a collection slot." in response.data
        assert Order.query.count() == 0
        
def test_checkout_rejects_invalid_collection_slot(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": "9999"
            }
        )

        assert response.status_code == 200
        assert b"Please choose a valid collection slot." in response.data
        assert Order.query.count() == 0
        
def test_checkout_rejects_slot_from_another_event(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        another_event = FoodEvent(
            name="Another Food Day",
            event_date=date(2026, 10, 17),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=False
        )

        db.session.add_all([
            event,
            another_event
        ])

        db.session.flush()

        slot = CollectionSlot(
            event_id=another_event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Please choose a valid collection slot." in response.data
        assert Order.query.count() == 0
        
def test_checkout_rejects_insufficient_stock(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=2,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 3
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Not enough Test Biryani available." in response.data
        assert Order.query.count() == 0
        
def test_checkout_rejects_inactive_item(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Unavailable Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=False
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Unavailable Biryani is no longer available." in response.data
        assert Order.query.count() == 0
        
def test_checkout_rejects_item_from_another_event(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        another_event = FoodEvent(
            name="Another Food Day",
            event_date=date(2026, 10, 17),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=False
        )

        db.session.add_all([
            event,
            another_event
        ])

        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=another_event.id,
            name="Wrong Event Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Wrong Event Biryani is no longer available." in response.data
        assert Order.query.count() == 0
        
def test_successful_checkout_updates_order_and_stock(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 3
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Collection",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200

        order = Order.query.first()

        assert order is not None
        assert order.total == 15.00
        assert order.fulfilment_method == "Collection"
        assert order.collection_slot_id == slot.id

        assert item.remaining_quantity == 7

        order_item = OrderItem.query.filter_by(
            order_id=order.id
        ).first()

        assert order_item is not None
        assert order_item.quantity == 3
        assert order_item.price_at_order == 5.00

        with client.session_transaction() as session:
            assert session["basket"] == {}
            
def test_checkout_rejects_delivery(client):

    with app.app_context():

        event = FoodEvent(
            name="Test Food Day",
            event_date=date(2026, 10, 10),
            collection_start_time=time(12, 0),
            collection_end_time=time(13, 0),
            collection_slot_duration=30,
            collection_slot_capacity=2,
            active=True
        )

        db.session.add(event)
        db.session.flush()

        slot = CollectionSlot(
            event_id=event.id,
            start_time=time(12, 0),
            end_time=time(12, 30),
            capacity=2
        )

        db.session.add(slot)

        item = MenuItem(
            event_id=event.id,
            name="Test Biryani",
            description="Test food",
            price=5.00,
            production_quantity=10,
            remaining_quantity=10,
            active=True
        )

        db.session.add(item)
        db.session.commit()

        with client.session_transaction() as session:
            session["basket"] = {
                str(item.id): 1
            }

        response = client.post(
            "/checkout",
            data={
                "name": "Test Customer",
                "phone": "07123456789",
                "fulfilment_method": "Delivery",
                "collection_slot": str(slot.id)
            }
        )

        assert response.status_code == 200
        assert b"Please choose a fulfilment method." in response.data
        assert Order.query.count() == 0