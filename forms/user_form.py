# forms/user_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional

# ユーザー登録・ログインフォーム (もし存在すれば)
class RegistrationForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    confirm_password = PasswordField('パスワード（確認）', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('登録')

class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

# ★★★ この新しいフォームクラスを追加します ★★★
class UserSearchForm(FlaskForm):
    search_query = StringField('検索キーワード', validators=[Optional(), Length(max=100)],
                               render_kw={"placeholder": "ユーザー名またはメールアドレスで検索"})
    submit = SubmitField('検索')