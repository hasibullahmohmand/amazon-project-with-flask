from flask import render_template, redirect, url_for, flash, request
from market import app, db
from market.module import Product, User, Cart, Order
from market.forms import LoginForm, RegisterForm, AddProduct, PlaceYourOrder
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy.orm import joinedload
from datetime import datetime, timedelta

with app.app_context():
    products = Product.query.all()

    
@app.route("/", methods=['GET','POST'])
@app.route("/products/<page>", methods=['GET','POST'])
@app.route('/search', methods=['GET','POST'])
def main_page(page=1):
    form = AddProduct()
    per_page = 30
    paginate_products = Product.query.paginate(page=int(page),per_page=per_page, error_out=False)
    
    searched_product = request.args.get("searched", "").strip()
    
    if searched_product:
        paginate_products = Product.query.filter(Product.product_name.ilike(f"%{searched_product}%")).paginate(page=int(page), per_page=per_page, error_out=False)
        if paginate_products.first:
            flash(f"Showing produts with '{searched_product}' keyword in them", category="success")
        else:
            flash(f"No products found with '{searched_product}' keyword in them", category="danger")
        
    if request.method == "POST":
        if current_user.is_authenticated:
            product_to_add = Cart(username=current_user.username,
                                        product_id=request.form.get('id'),
                                        quantity=request.form.get('quantity-selector')
                                        )
            db.session.add(product_to_add)
            db.session.commit()
            flash(f"{request.form.get('quantity-selector')} Product was added to cart!", category="success")
            return redirect(url_for('cart_page'))
        else:
            flash("Cannot add the product to the cart! Login required", category="danger")
            return redirect(url_for('login_page'))
        
        
    return render_template('index.html', products=paginate_products.items, pagination=paginate_products,form=form, cart_items_count=cart_item_count())

@app.route("/orders", methods=['GET','POST'])
@login_required
def order_page():
    ordered_items = db.session.query(Order).options(joinedload(Order.product)).filter(Order.username == current_user.username).all()
    items = [
        {
            'id': ordered_item.id,
            'image': ordered_item.product.image,
            'product_id': ordered_item.product_id,
            'product_name': ordered_item.product.product_name,
            'total_price': ordered_item.quantity * ordered_item.product.selling_price + int(0.1 * ordered_item.quantity * ordered_item.product.selling_price),
            'quantity': ordered_item.quantity,
            'delivery_date': ordered_item.delivery_date,
            'order_date': ordered_item.order_date,
            'shipping_cost': ordered_item.shipping_cost,
        } for ordered_item in ordered_items ]
    
    selected_option = request.form.get('action') 
    product_id = request.form.get('id')
    if selected_option == "buy-agian":
        product_to_buy_agian = Cart(username=current_user.username,
                                      product_id=request.form.get('id'),
                                      quantity=1
                                      )
        db.session.add(product_to_buy_agian)
        db.session.commit()
        flash(f"The product was added to cart!", category="success")
        return redirect(url_for('cart_page'))
    if selected_option == "track":
        flash(f"This option will be avalible soon!", category="danger")
        return redirect(url_for('order_page'))

    return render_template("orders.html", items=items, cart_items_count=cart_item_count())

@app.route("/cart", methods=['GET','POST'])
@login_required
def cart_page():
    cart_items = db.session.query(Cart).options(joinedload(Cart.product)).filter(Cart.username == current_user.username).all()
    form = PlaceYourOrder()
    
    items = [
        {
            'selling_price': cart_item.product.selling_price,
            'image': cart_item.product.image,
            'product_id': cart_item.product_id,
            'product_name': cart_item.product.product_name,
            'total_price': cart_item.quantity * cart_item.product.selling_price,
            'quantity': cart_item.quantity,
            'delivery_date': cart_item.delivery_date,
            'shipping_cost': cart_item.shipping_cost,
            'total_tax': int(cart_item.quantity * cart_item.product.selling_price * 0.1)
        } for cart_item in cart_items 
                ]
       
    selected_option = request.form.get('option') 
    action = request.form.get('action') 
    quantity = request.form.get('quantity-selector') 
    fdate = datetime.now().date() 

    if selected_option == '0':
        fdate = datetime.now().date() + timedelta(3)
    elif selected_option == '499':
        fdate = datetime.now().date() + timedelta(2)
    elif selected_option == '999':
        fdate = datetime.now().date() + timedelta(1)
    

    if action == 'update':
        product_to_change = Cart.query.filter_by(product_id=request.form.get('product_id')).first()
        flash("Product updated successfully", category="success")
        product_to_change.shipping_cost = int(selected_option)
        product_to_change.delivery_date = fdate
        product_to_change.quantity = int(quantity)
        db.session.commit()
        return redirect(url_for('cart_page'))
    elif action == 'delete':
        flash(f"Product deleted successfully!", category="danger")
        product_to_delete = Cart.query.filter_by(product_id=request.form.get('product_id')).first()
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect(url_for('cart_page'))
    
    if request.method == "POST":
        if form.validate_on_submit:
            products_to_order = Cart.query.filter_by(username=current_user.username).all()
            total_price = sum(int(item['quantity']) * item['total_price'] for item in items) 
            shipping_price = sum(int(item['shipping_cost']) for item in items)
            if products_to_order:
                total_price = total_price + int(total_price * 0.1) + shipping_price
                if current_user.buget > total_price:
                    flash(f"Order placed succesfully!: {datetime.now().date().strftime('%b %d')}", category="success")
                    for product in products_to_order: 
                        product_to_order = Order(username=current_user.username,
                                                product_id=product.product_id,
                                                quantity=product.quantity,
                                                delivery_date=product.delivery_date,
                                                order_date=datetime.now().date(),
                                                shipping_cost=product.shipping_cost,                           
                        )
                        current_user.buget -= total_price
                        db.session.add(product_to_order)
                        db.session.delete(product)
                    db.session.commit()
                    return redirect(url_for('order_page'))
                else:
                    flash(f"Cannot place order! Insufficient balance", category="danger")
                    return redirect(url_for('cart_page'))
            else:
                flash("Cannot place order! There is no products in the cart!", category="danger")
                return redirect(url_for('cart_page'))
    return render_template("cart.html",items=items, datetime=datetime, timedelta=timedelta, form=form, cart_items_count=cart_item_count())

@app.route("/register", methods=['GET','POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_add = User(username=form.username.data, 
                           email=form.email.data,
                           password=form.password1.data)
        db.session.add(user_to_add)
        db.session.commit()
        flash(f"Registration successfull! You are logged in as {form.username.data}", category="success")
        login_user(user_to_add)
        return redirect(url_for("main_page"))
    if form.errors != {}:
        for error in form.errors.values():
            if error[0] == 'Field must be equal to password1.':
                flash("An error accured while registiring: Passwords are not mataching!", category="danger")
            else:
                flash(f"An error accured while registiring: {error[0]}", category="danger")
    return render_template("register.html", form=form, cart_items_count=cart_item_count())

@app.route("/login", methods=['GET','POST'])
def login_page():
    form = LoginForm()
    if request.method == "POST":
        if form.validate_on_submit():
            attempted_user = User.query.filter_by(username=form.username.data).first()
            if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data): 
                login_user(attempted_user)
                flash(f"Login successfull! Welcome back {attempted_user.username}", category="success")
                return redirect(url_for("main_page"))
            else:
                flash("Wrong username or password! Please check your username or password", category="danger")
        
    return render_template("login.html", form=form, cart_items_count=cart_item_count())

@app.route("/logout")
def logout_page():
    flash(f"{current_user.username} loged out successfully!", category="success")
    logout_user()
    return redirect(url_for("main_page"))
    

def sumT(items):
    total = 0
    for item in items:
        total += item['total_price']
    return total

def sumShip(items):
    total = 0
    for item in items:
        total += item['shipping_cost']
    return total

def sumTT(items):
    total = 0
    for item in items:
        total += item['total_tax']
    return total

def cart_item_count():
    if current_user.is_authenticated:
        return Cart.query.filter_by(username=current_user.username).count()
    else: 
         return  0
 
app.jinja_env.filters['sumT'] = sumT
app.jinja_env.filters['sumShip'] = sumShip
app.jinja_env.filters['sumTT'] = sumTT


