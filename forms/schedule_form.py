# forms/schedule_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateTimeLocalField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import DateTimeLocalInput

class ScheduleForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('説明', validators=[Length(max=500)])
    start_time = DateTimeLocalField('開始日時', validators=[DataRequired()], format='%Y-%m-%dT%H:%M', widget=DateTimeLocalInput())
    end_time = DateTimeLocalField('終了日時', format='%Y-%m-%dT%H:%M', widget=DateTimeLocalInput(), description="空欄の場合、開始日時が終了日時として扱われます。")
    all_day = BooleanField('終日イベント') # ★追加されたフィールド★
    submit = SubmitField('保存')