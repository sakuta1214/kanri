# forms/customer_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional

class CustomerForm(FlaskForm):
    name = StringField('顧客名', validators=[DataRequired(), Length(max=100)])
    email = StringField('メールアドレス', validators=[Optional(), Email(), Length(max=120)])
    phone = StringField('電話番号', validators=[Optional(), Length(max=20)])
    address = StringField('住所', validators=[Optional(), Length(max=200)])
    company = StringField('所属会社', validators=[Optional(), Length(max=100)])
    submit = SubmitField('登録')