# forms/task_form.py

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Optional
from wtforms_sqlalchemy.fields import QuerySelectField # 担当者選択に使用する場合

# もしTaskモデルにstatusフィールドがある場合、その選択肢を定義
# (例: '未完了', '進行中', '完了')
# STATUS_CHOICES = [
#     ('todo', '未完了'),
#     ('in_progress', '進行中'),
#     ('done', '完了')
# ]

class TaskForm(FlaskForm):
    title = StringField('タスク名', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('詳細', validators=[Optional(), Length(max=500)])
    due_date = DateTimeLocalField('期日', format='%Y-%m-%dT%H:%M', validators=[Optional()])
    # statusフィールドを追加している場合
    status = SelectField('ステータス', choices=[('todo', '未完了'), ('in_progress', '進行中'), ('done', '完了')], validators=[DataRequired()])
    # user_id = QuerySelectField('担当者', query_factory=lambda: User.query.all(), get_pk=lambda a: a.id, get_label=lambda a: a.username, allow_blank=True, blank_text='-- 担当者を選択 --')
    submit = SubmitField('保存')

# ★★★ この新しいフォームクラスを追加します ★★★
class TaskSearchForm(FlaskForm):
    search_query = StringField('検索キーワード', validators=[Optional(), Length(max=100)])
    # 'すべて' を含む選択肢
    status_filter = SelectField('ステータス', choices=[
        ('', 'すべて'),  # 値が空文字列の場合、「すべて」を意味する
        ('todo', '未完了'),
        ('in_progress', '進行中'),
        ('done', '完了')
    ], validators=[Optional()])
    submit = SubmitField('検索')