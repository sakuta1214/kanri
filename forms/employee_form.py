# forms/employee_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp
from wtforms.widgets import DateInput # HTML5 date input を使う場合

class EmployeeForm(FlaskForm):
    # ★★★ この行を追加 ★★★
    full_name = StringField('氏名', validators=[DataRequired(), Length(max=100)])

    email = StringField('メールアドレス', validators=[DataRequired(), Email(), Length(max=120)])
    phone_number = StringField('電話番号', validators=[Length(max=20), Regexp(r'^\+?\d{10,15}$', message='有効な電話番号を入力してください。', flags=0)], render_kw={"placeholder": "例: 09012345678"})
    department = StringField('部署', validators=[Length(max=50)])
    position = StringField('役職', validators=[Length(max=50)])
    hire_date = DateField('入社日', validators=[DataRequired()], format='%Y-%m-%d', widget=DateInput())
    submit = SubmitField('保存')