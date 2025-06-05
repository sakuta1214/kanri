# forms/auth_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from models.user import User # Userモデルをインポート

class RegisterForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    password = PasswordField('パスワード', validators=[DataRequired(), Length(min=6, max=200)])
    confirm_password = PasswordField('パスワード（確認）', validators=[DataRequired(), EqualTo('password', message='パスワードが一致しません。')])
    role = SelectField('役割', choices=[('一般ユーザー', '一般ユーザー'), ('管理者', '管理者')], validators=[DataRequired()]) # ★ 追加
    submit = SubmitField('登録')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('このユーザー名は既に使われています。')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('このメールアドレスは既に登録されています。')

class LoginForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

# ユーザー編集フォームも追加
class EditUserForm(FlaskForm):
    username = StringField('ユーザー名', validators=[DataRequired(), Length(min=4, max=80)])
    email = StringField('メールアドレス', validators=[DataRequired(), Email()])
    # パスワードは任意で変更できるようにOptionalにするか、別のフォームにするのが一般的
    # ここでは既存のパスワードは変更しない前提とする
    role = SelectField('役割', choices=[('一般ユーザー', '一般ユーザー'), ('管理者', '管理者')], validators=[DataRequired()]) # ★ 追加
    submit = SubmitField('更新')

    # 既存のユーザーIDを受け取るためのフィールド
    user_id = StringField(validators=[Optional()]) # 編集時に使用

    def validate_username(self, username):
        from flask import request
        user = User.query.filter_by(username=username.data).first()
        # 編集対象のユーザー自身の場合はチェックしない
        if user and str(user.id) != self.user_id.data:
            raise ValidationError('このユーザー名は既に使われています。')

    def validate_email(self, email):
        from flask import request
        user = User.query.filter_by(email=email.data).first()
        # 編集対象のユーザー自身の場合はチェックしない
        if user and str(user.id) != self.user_id.data:
            raise ValidationError('このメールアドレスは既に登録されています。')