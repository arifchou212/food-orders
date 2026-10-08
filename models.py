from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FoodEvent(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    event_date = db.Column(
        db.Date,
        nullable=False
    )
    
    collection_start_time = db.Column(
        db.Time,
        nullable=False
    )

    collection_end_time = db.Column(
        db.Time,
        nullable=False
    )

    collection_slot_duration = db.Column(
        db.Integer,
        nullable=False
    )

    collection_slot_capacity = db.Column(
        db.Integer,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=False,
        nullable=False
    )

    menu_items = db.relationship(
        "MenuItem",
        backref="event",
        cascade="all, delete-orphan"
    )
    
class CollectionSlot(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("food_event.id"),
        nullable=False
    )

    start_time = db.Column(
        db.Time,
        nullable=False
    )

    end_time = db.Column(
        db.Time,
        nullable=False
    )

    capacity = db.Column(
        db.Integer,
        nullable=False,
        default=5
    )

    event = db.relationship(
        "FoodEvent",
        backref=db.backref(
            "collection_slots",
            cascade="all, delete-orphan"
        )
    )

class MenuItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("food_event.id"),
        nullable=False
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(500)
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    production_quantity = db.Column(
        db.Integer,
        nullable=False
    )

    remaining_quantity = db.Column(
        db.Integer,
        nullable=False
    )

    active = db.Column(
        db.Boolean,
        default=True,
        nullable=False
    )
    
    image_filename = db.Column(
    db.String(255),
    nullable=True
    )

class Customer(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(30),
        nullable=False
    )

class Order(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    event_id = db.Column(
        db.Integer,
        db.ForeignKey("food_event.id"),
        nullable=False
    )

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey("customer.id"),
        nullable=False
    )

    total = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="New"
    )

    fulfilment_method = db.Column(
        db.String(20),
        nullable=False,
        default="Collection"
    )

    collection_slot_id = db.Column(
        db.Integer,
        db.ForeignKey("collection_slot.id"),
        nullable=False
    )

    customer = db.relationship(
        "Customer"
    )

    event = db.relationship(
        "FoodEvent"
    )
    
    collection_slot = db.relationship(
        "CollectionSlot"
    )

class OrderItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    menu_item_id = db.Column(
        db.Integer,
        db.ForeignKey("menu_item.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    price_at_order = db.Column(
        db.Float,
        nullable=False
    )


    menu_item = db.relationship(
        "MenuItem"
    )