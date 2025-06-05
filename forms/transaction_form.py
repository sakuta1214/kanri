# forms/transaction_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from wtforms.widgets import DateInput
import datetime

class TransactionForm(FlaskForm):
    transaction_date = DateField('取引日', format='%Y-%m-%d', validators=[DataRequired()], widget=DateInput())
    type = SelectField('種類', choices=[('収入', '収入'), ('支出', '支出')], validators=[DataRequired()])
    category = StringField('カテゴリ', validators=[DataRequired(), Length(max=100)])
    amount = FloatField('金額', validators=[DataRequired(), NumberRange(min=0.01, message='金額は0より大きい値である必要があります。')])
    description = TextAreaField('メモ', validators=[Optional()])
    submit = SubmitField('登録')