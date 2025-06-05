# forms/document_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileRequired, FileAllowed # FileRequired は UploadDocumentForm でのみ使用

class UploadDocumentForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('説明', validators=[Length(max=500)])
    file = FileField('ファイル', validators=[FileRequired(), FileAllowed(['pdf', 'doc', 'docx', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'], '許可されていないファイル形式です！')])
    submit = SubmitField('アップロード')

# ★★★ この EditDocumentForm を追加します ★★★
class EditDocumentForm(FlaskForm):
    title = StringField('タイトル', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('説明', validators=[Length(max=500)])
    # ファイルは必須ではないため、FileRequiredは削除
    # 必要に応じて、FileAllowedは残しておく
    file = FileField('新しいファイル', validators=[FileAllowed(['pdf', 'doc', 'docx', 'xlsx', 'txt', 'jpg', 'jpeg', 'png'], '許可されていないファイル形式です！')])
    submit = SubmitField('更新')