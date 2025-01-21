from flask import Flask, render_template, redirect
from flask_wtf.csrf import CSRFProtect
from config import Config
from app.shipping_form import ShippingForm

app = Flask(__name__)
app.config.from_object(Config)
csrf = CSRFProtect(app)

@app.route('/')
def root():
    return '<h1>Package Tracker</h1>'

@app.route('/new_package', methods=['GET', 'POST'])
def new_package():
    form = ShippingForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('shipping_request.html', form=form)