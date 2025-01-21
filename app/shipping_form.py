from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from map.map import map

class shipping_form(FlaskForm):
    name_sender=StringField("Sender Name", validators=[DataRequired()])
    name_recipient=StringField("Recipient Name", validators=[DataRequired()])
    origin=SelectField("Origin",
        choices=[("", "Option 1"), ("option2", "Option 2"), ("option3", "Option 3")],)
    destination=SelectField("Destination", validators=[DataRequired()])
    express=BooleanField()

    submit=SubmitField("Submit")
    cancel=SubmitField("Cancel")