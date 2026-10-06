from datetime import datetime

import os
from dotenv import load_dotenv

from flask import (
    Flask,
    render_template,
    session,
    redirect,
    url_for,
    request
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from flask_wtf.csrf import CSRFProtect

from models import (
    db,
    FoodEvent,
    MenuItem,
    Customer,
    Order,
    OrderItem
)


app = Flask(__name__)

load_dotenv()

app.secret_key = os.getenv("FLASK_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///food_orders.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

csrf = CSRFProtect(app)

db.init_app(app)


with app.app_context():
    db.create_all()


# =========================================
# Customer: Home
# =========================================

@app.route("/")
def home():

    event = FoodEvent.query.filter_by(
        active=True
    ).order_by(
        FoodEvent.event_date.asc()
    ).first()

    if event:

        menu_items = MenuItem.query.filter_by(
            event_id=event.id,
            active=True
        ).all()

    else:

        menu_items = []


    return render_template(
        "index.html",
        event=event,
        menu_items=menu_items
    )


# =========================================
# Customer: Basket
# =========================================

@app.route(
    "/basket/add/<int:item_id>",
    methods=["POST"]
)
def basket_add(item_id):

    item = MenuItem.query.get_or_404(item_id)


    if not item.active:
        return redirect(url_for("home"))


    basket = session.get("basket", {})

    item_id = str(item.id)

    current_quantity = basket.get(
        item_id,
        0
    )


    if (
        item.remaining_quantity is not None
        and current_quantity >= item.remaining_quantity
    ):
        return redirect(url_for("basket"))


    basket[item_id] = current_quantity + 1

    session["basket"] = basket


    return redirect(url_for("basket"))


@app.route(
    "/basket/remove-one/<int:item_id>",
    methods=["POST"]
)
def basket_remove_one(item_id):

    basket = session.get("basket", {})

    item_id = str(item_id)


    if item_id in basket:

        basket[item_id] -= 1


        if basket[item_id] <= 0:
            del basket[item_id]


        session["basket"] = basket


    return redirect(url_for("basket"))


@app.route(
    "/basket/delete/<int:item_id>",
    methods=["POST"]
)
def basket_delete(item_id):

    basket = session.get("basket", {})

    item_id = str(item_id)


    if item_id in basket:
        del basket[item_id]


    session["basket"] = basket


    return redirect(url_for("basket"))


@app.route("/basket")
def basket():

    basket = session.get("basket", {})

    basket_items = []

    total = 0


    for item_id, quantity in basket.items():

        item = MenuItem.query.get(
            int(item_id)
        )


        if item:

            subtotal = (
                item.price * quantity
            )

            total += subtotal


            basket_items.append({
                "item": item,
                "quantity": quantity,
                "subtotal": subtotal
            })


    return render_template(
        "basket.html",
        basket_items=basket_items,
        total=total
    )


# =========================================
# Customer: Checkout
# =========================================

@app.route(
    "/checkout",
    methods=["GET", "POST"]
)
def checkout():

    basket = session.get("basket", {})


    if not basket:
        return redirect(url_for("home"))


    event = FoodEvent.query.filter_by(
        active=True
    ).order_by(
        FoodEvent.event_date.asc()
    ).first()


    if not event:
        return redirect(url_for("home"))


    basket_items = []

    total = 0


    for item_id, quantity in basket.items():

        item = MenuItem.query.get(
            int(item_id)
        )


        if not item:
            return redirect(url_for("basket"))

        subtotal = (
            item.price * quantity
        )

        total += subtotal


        basket_items.append({
            "item": item,
            "quantity": quantity,
            "subtotal": subtotal
        })


    if request.method == "POST":

        # ---------------------------------
        # Validate basket quantities
        # ---------------------------------

        for entry in basket_items:

            item = entry["item"]

            quantity = entry["quantity"]
            
            # Quantity must be a positive whole number
            
            if not isinstance(quantity, int) or quantity < 1:
                return render_template(
                    "checkout.html",
                    basket_items=basket_items,
                    total=total,
                    error=(
                        f"Invalid quantity for "
                        f"{item.name}."
                    )
                )


            if (
                not item.active
                or item.event_id != event.id
            ):
                return render_template(
                    "checkout.html",
                    basket_items=basket_items,
                    total=total,
                    error=(
                        f"{item.name} is no longer "
                        "available."
                    )
                )


            if (
                item.remaining_quantity is not None
                and quantity > item.remaining_quantity
            ):
                return render_template(
                    "checkout.html",
                    basket_items=basket_items,
                    total=total,
                    error=(
                        f"Not enough {item.name} "
                        "available."
                    )
                )


        # ---------------------------------
        # Customer details
        # ---------------------------------

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()


        if not name or not phone:

            return render_template(
                "checkout.html",
                basket_items=basket_items,
                total=total,
                error=(
                    "Please enter your name "
                    "and phone number."
                )
            )
            
        if len(phone) < 7 or len(phone) > 15:

            return render_template(
                "checkout.html",
                basket_items=basket_items,
                total=total,
                error=(
                    "Please enter a valid "
                    "phone number."
                )
            )
        
        if len(name) < 2 or len(name) > 100:

            return render_template(
                "checkout.html",
                basket_items=basket_items,
                total=total,
                error=(
                    "Please enter a valid "
                    "name."
                )
            )


        # ---------------------------------
        # Fulfilment
        # ---------------------------------

        fulfilment_method = request.form.get(
            "fulfilment_method"
        )


        if fulfilment_method != "Collection":

            return render_template(
                "checkout.html",
                basket_items=basket_items,
                total=total,
                error=(
                    "Please choose a fulfilment "
                    "method."
                )
            )


        collection_slot = request.form.get(
            "collection_slot"
        )


        if not collection_slot:

            return render_template(
                "checkout.html",
                basket_items=basket_items,
                total=total,
                error=(
                    "Please choose a "
                    "collection slot."
                )
            )


        delivery_address = None


        # else:

        #     collection_slot = None

        #     delivery_address = request.form.get(
        #         "delivery_address",
        #         ""
        #     ).strip()


        #     if not delivery_address:

        #         return render_template(
        #             "checkout.html",
        #             basket_items=basket_items,
        #             total=total,
        #             error=(
        #                 "Please enter your "
        #                 "delivery address."
        #             )
        #         )


        # ---------------------------------
        # Create customer
        # ---------------------------------

        customer = Customer(
            name=name,
            phone=phone
        )

        db.session.add(customer)

        db.session.flush()


        # ---------------------------------
        # Create order
        # ---------------------------------

        order = Order(
            event_id=event.id,
            customer_id=customer.id,
            total=total,
            status="New",
            fulfilment_method=fulfilment_method,
            collection_slot=collection_slot,
            delivery_address=delivery_address
        )

        db.session.add(order)

        db.session.flush()


        # ---------------------------------
        # Create order items
        # ---------------------------------

        for entry in basket_items:

            item = entry["item"]

            quantity = entry["quantity"]


            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                quantity=quantity,
                price_at_order=item.price
            )


            db.session.add(order_item)


            item.remaining_quantity -= quantity


        db.session.commit()


        # Empty basket after successful order

        session["basket"] = {}


        return render_template(
            "order_confirmation.html",
            order=order
        )


    return render_template(
        "checkout.html",
        basket_items=basket_items,
        total=total
    )


# =========================================
# Admin: Login
# =========================================

@app.route(
    "/admin/login",
    methods=["GET", "POST"]
)
def admin_login():

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        stored_hash = os.getenv(
            "ADMIN_PASSWORD_HASH"
        )


        if (
            username == os.getenv("ADMIN_USERNAME")
            and stored_hash
            and check_password_hash(
                stored_hash,
                password
            )
        ):

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )


        return render_template(
            "admin_login.html",
            error=(
                "Incorrect username or password."
            )
        )


    return render_template(
        "admin_login.html"
    )


@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin_login")
    )


# =========================================
# Admin: Dashboard
# =========================================

@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )


    # ---------------------------------
    # Current active event
    # ---------------------------------

    event = FoodEvent.query.filter_by(
        active=True
    ).order_by(
        FoodEvent.event_date.asc()
    ).first()


    # ---------------------------------
    # Previous events
    # ---------------------------------

    previous_events = FoodEvent.query.filter(
        FoodEvent.active == False
    ).order_by(
        FoodEvent.event_date.desc()
    ).all()


    # ---------------------------------
    # No active event
    # ---------------------------------

    if not event:

        return render_template(
            "admin.html",
            event=None,
            orders=[],
            previous_events=previous_events,
            food_totals={},
            total_revenue=0,
            new_orders=0,
            preparing_orders=0,
            ready_orders=0,
            collected_orders=0
        )


    # ---------------------------------
    # Current event orders
    # ---------------------------------

    orders = Order.query.filter_by(
        event_id=event.id
    ).order_by(
        Order.id.desc()
    ).all()


    food_totals = {}

    total_revenue = 0


    new_orders = 0
    preparing_orders = 0
    ready_orders = 0
    collected_orders = 0


    # ---------------------------------
    # Process current event orders
    # ---------------------------------

    for order in orders:

        # Revenue
        if order.status != "Cancelled":

            total_revenue += order.total


        # Order status counts
        if order.status == "New":

            new_orders += 1

        elif order.status == "Preparing":

            preparing_orders += 1

        elif order.status == "Ready":

            ready_orders += 1

        elif order.status == "Collected":

            collected_orders += 1


        # Food preparation totals
        if order.status != "Cancelled":

            order_items = OrderItem.query.filter_by(
                order_id=order.id
            ).all()


            for order_item in order_items:

                item = MenuItem.query.get(
                    order_item.menu_item_id
                )


                if item:

                    if item.name not in food_totals:

                        food_totals[item.name] = 0


                    food_totals[item.name] += (
                        order_item.quantity
                    )


    return render_template(
        "admin.html",
        event=event,
        orders=orders,
        previous_events=previous_events,
        food_totals=food_totals,
        total_revenue=total_revenue,
        new_orders=new_orders,
        preparing_orders=preparing_orders,
        ready_orders=ready_orders,
        collected_orders=collected_orders
    )

# =========================================
# Admin: Update Order Status
# =========================================

@app.route(
    "/admin/order/<int:order_id>/status",
    methods=["POST"]
)
def update_order_status(order_id):

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    order = Order.query.get_or_404(
        order_id
    )


    new_status = request.form.get(
        "status"
    )


    allowed_statuses = [
        "New",
        "Preparing",
        "Ready",
        "Collected",
        "Cancelled"
    ]


    if new_status not in allowed_statuses:

        return redirect(
            url_for("admin")
        )


    old_status = order.status


    # Nothing needs to change
    if old_status == new_status:

        return redirect(
            url_for("admin")
        )


    # ---------------------------------
    # Prevent cancelling an order
    # that has already been collected
    # ---------------------------------

    if (
        old_status == "Collected"
        and new_status == "Cancelled"
    ):

        return redirect(
            url_for("admin")
        )


    # ---------------------------------
    # Get items in the order
    # ---------------------------------

    order_items = OrderItem.query.filter_by(
        order_id=order.id
    ).all()


    # ---------------------------------
    # Cancelling an order
    # ---------------------------------

    if (
        new_status == "Cancelled"
        and old_status != "Cancelled"
    ):

        for order_item in order_items:

            item = db.session.get(
                MenuItem,
                order_item.menu_item_id
            )


            if item:

                item.remaining_quantity += (
                    order_item.quantity
                )


    # ---------------------------------
    # Re-opening a cancelled order
    # ---------------------------------

    elif (
        old_status == "Cancelled"
        and new_status != "Cancelled"
    ):

        # First check that enough stock exists
        # for the whole order.

        for order_item in order_items:

            item = db.session.get(
                MenuItem,
                order_item.menu_item_id
            )


            if not item:

                return redirect(
                    url_for("admin")
                )


            if (
                item.remaining_quantity
                < order_item.quantity
            ):

                return redirect(
                    url_for("admin")
                )


        # Only change stock after we know
        # the entire order can be fulfilled.

        for order_item in order_items:

            item = db.session.get(
                MenuItem,
                order_item.menu_item_id
            )


            item.remaining_quantity -= (
                order_item.quantity
            )


    # ---------------------------------
    # Update order status
    # ---------------------------------

    order.status = new_status

    db.session.commit()


    return redirect(
        url_for("admin")
    )

# =========================================
# Admin: Order Details
# =========================================

@app.route(
    "/admin/order/<int:order_id>"
)
def order_details(order_id):

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    order = Order.query.get_or_404(
        order_id
    )


    order_items = OrderItem.query.filter_by(
        order_id=order.id
    ).all()


    return render_template(
        "order_details.html",
        order=order,
        order_items=order_items
    )

@app.route("/admin/event/<int:event_id>/orders")
def event_orders(event_id):

    if not session.get("admin_logged_in"):
        return redirect(
            url_for("admin_login")
        )


    # Find the event
    event = db.session.get(
        FoodEvent,
        event_id
    )


    if not event:
        return "Food event not found", 404


    # Get all orders for this event
    orders = Order.query.filter_by(
        event_id=event.id
    ).order_by(
        Order.id.desc()
    ).all()


    # Calculate revenue
    total_revenue = 0

    for order in orders:

        if order.status != "Cancelled":

            total_revenue += order.total


    return render_template(
        "event_orders.html",
        event=event,
        orders=orders,
        total_revenue=total_revenue
    )


# =========================================
# Admin: Menu Management
# =========================================

@app.route("/admin/menu")
def admin_menu():

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    events = FoodEvent.query.order_by(
        FoodEvent.event_date.desc()
    ).all()


    return render_template(
        "admin_menu.html",
        events=events
    )


# =========================================
# Admin: Add Menu Item
# =========================================

@app.route(
    "/admin/menu/<int:event_id>/add",
    methods=["GET", "POST"]
)
def add_menu_item(event_id):

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    event = FoodEvent.query.get_or_404(
        event_id
    )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()


        try:

            price = float(
                request.form["price"]
            )

            production_quantity = int(
                request.form[
                    "production_quantity"
                ]
            )

        except (
            ValueError,
            KeyError
        ):

            return render_template(
                "add_menu_item.html",
                event=event,
                error=(
                    "Please enter valid "
                    "price and quantity values."
                )
            )


        if price < 0:

            return render_template(
                "add_menu_item.html",
                event=event,
                error=(
                    "Price cannot be negative."
                )
            )


        if production_quantity < 0:

            return render_template(
                "add_menu_item.html",
                event=event,
                error=(
                    "Production quantity "
                    "cannot be negative."
                )
            )


        if not name:

            return render_template(
                "add_menu_item.html",
                event=event,
                error=(
                    "Please enter a food name."
                )
            )


        item = MenuItem(
            event_id=event.id,
            name=name,
            description=description,
            price=price,
            production_quantity=(
                production_quantity
            ),
            remaining_quantity=(
                production_quantity
            ),
            active=True
        )


        db.session.add(item)

        db.session.commit()


        return redirect(
            url_for("admin_menu")
        )


    return render_template(
        "add_menu_item.html",
        event=event
    )


# =========================================
# Admin: Edit Menu Item
# =========================================

@app.route(
    "/admin/menu/item/<int:item_id>/edit",
    methods=["GET", "POST"]
)
def edit_menu_item(item_id):

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    item = MenuItem.query.get_or_404(
        item_id
    )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()


        try:

            price = float(
                request.form["price"]
            )

            new_production_quantity = int(
                request.form[
                    "production_quantity"
                ]
            )

        except (
            ValueError,
            KeyError
        ):

            return render_template(
                "edit_menu_item.html",
                item=item,
                error=(
                    "Please enter valid "
                    "price and quantity values."
                )
            )


        if not name:

            return render_template(
                "edit_menu_item.html",
                item=item,
                error=(
                    "Please enter a food name."
                )
            )


        if price < 0:

            return render_template(
                "edit_menu_item.html",
                item=item,
                error=(
                    "Price cannot be negative."
                )
            )


        if new_production_quantity < 0:

            return render_template(
                "edit_menu_item.html",
                item=item,
                error=(
                    "Production quantity "
                    "cannot be negative."
                )
            )


        # ---------------------------------
        # Preserve existing orders
        # ---------------------------------

        ordered_quantity = (
            item.production_quantity
            - item.remaining_quantity
        )


        if (
            new_production_quantity
            < ordered_quantity
        ):

            return render_template(
                "edit_menu_item.html",
                item=item,
                error=(
                    "Production quantity "
                    f"cannot be less than "
                    f"{ordered_quantity}, "
                    "which has already "
                    "been ordered."
                )
            )


        item.name = name

        item.description = description

        item.price = price

        item.production_quantity = (
            new_production_quantity
        )

        item.remaining_quantity = (
            new_production_quantity
            - ordered_quantity
        )


        db.session.commit()


        return redirect(
            url_for("admin_menu")
        )


    return render_template(
        "edit_menu_item.html",
        item=item
    )


# =========================================
# Admin: Remove Menu Item
# =========================================

@app.route(
    "/admin/menu/item/<int:item_id>/delete",
    methods=["POST"]
)
def delete_menu_item(item_id):

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    item = MenuItem.query.get_or_404(
        item_id
    )


    item.active = False


    db.session.commit()


    return redirect(
        url_for("admin_menu")
    )


# =========================================
# Admin: Create Food Day
# =========================================

@app.route(
    "/admin/menu/create",
    methods=["GET", "POST"]
)
def create_food_event():

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()


        if not name:

            return render_template(
                "create_food_event.html",
                error=(
                    "Please enter a food "
                    "day name."
                )
            )


        try:

            event_date = datetime.strptime(
                request.form["event_date"],
                "%Y-%m-%d"
            ).date()

        except (
            ValueError,
            KeyError
        ):

            return render_template(
                "create_food_event.html",
                error=(
                    "Please enter a valid date."
                )
            )


        # New food days are inactive.
        # The admin can activate them separately.

        event = FoodEvent(
            name=name,
            event_date=event_date,
            active=False
        )


        db.session.add(event)

        db.session.commit()


        return redirect(
            url_for("admin_menu")
        )


    return render_template(
        "create_food_event.html"
    )


# =========================================
# Admin: Activate / Deactivate Food Day
# =========================================

@app.route(
    "/admin/menu/event/<int:event_id>/toggle",
    methods=["POST"]
)
def toggle_food_event(event_id):

    if not session.get(
        "admin_logged_in"
    ):
        return redirect(
            url_for("admin_login")
        )


    event = FoodEvent.query.get_or_404(
        event_id
    )


    if event.active:

        event.active = False

    else:

        # Deactivate every other event
        # before activating this one.

        FoodEvent.query.filter_by(
            active=True
        ).update({
            "active": False
        })


        event.active = True


    db.session.commit()


    return redirect(
        url_for("admin_menu")
    )


# =========================================
# Run Application
# =========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )