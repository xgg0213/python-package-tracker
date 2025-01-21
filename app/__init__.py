from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from app.shipping_form import ShippingForm
from app.auth_forms import LoginForm, SignUpForm
from flask_migrate import Migrate
from app.models import db, Package, User
from map.map import DELIVERED
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@login_required
def root():
    print("=== ROOT ROUTE HIT ===")  # Basic debug print
    
    # Get filter and sort parameters
    filter_by = request.args.get('filter', 'all')
    sort_by = request.args.get('sort', 'id')
    
    print(f"Debug - filter_by: {filter_by}")
    print(f"Debug - sort_by: {sort_by}")
    print(f"Debug - request.args: {request.args}")
    
    # Base query
    query = Package.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if filter_by == 'delivered':
        query = query.filter_by(location=DELIVERED)
    elif filter_by == 'in_transit':
        query = query.filter(Package.location != DELIVERED)
    
    # Apply sorting
    if sort_by == 'sender':
        query = query.order_by(Package.sender)
    elif sort_by == 'recipient':
        query = query.order_by(Package.recipient)
    elif sort_by == 'location':
        query = query.order_by(Package.location)
    else:  # default sort by id
        query = query.order_by(Package.id)
    
    packages = query.all()
    
    # Create a form instance for CSRF token
    form = FlaskForm()
    
    print(f"Debug - Rendering with filter_by={filter_by}, sort_by={sort_by}")
    
    return render_template('package_status.html', 
                         packages=packages, 
                         filter_by=filter_by,
                         sort_by=sort_by,
                         form=form)

@app.route('/new_package', methods=['GET', 'POST'])
@login_required
def new_package():
    form = ShippingForm()
    if form.validate_on_submit():
        data = form.data
        new_package = Package(
            sender=data['sender_name'],
            recipient=data['recipient_name'],
            origin=data['origin'],
            destination=data['destination'],
            location=data['origin'],
            user_id=current_user.id
        )
        db.session.add(new_package)
        Package.advance_all_locations()
        db.session.commit()
        return redirect('/')
    return render_template('shipping_request.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('root'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('root'))
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/delete_package/<int:id>', methods=['POST'])
@login_required
def delete_package(id):
    # Find package or return 404 if not found
    package = Package.query.get_or_404(id)
    
    # Security check: ensure user owns the package
    if package.user_id != current_user.id:
        return "Unauthorized", 403
        
    # Delete the package
    db.session.delete(package)
    db.session.commit()
    
    # Redirect back to package list
    return redirect(url_for('root'))