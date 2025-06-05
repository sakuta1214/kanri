# forms/project_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from wtforms.widgets import DateInput

# カスタムバリデーター：終了日が開始日より後であることを確認
def validate_end_date_after_start(form, field):
    if form.start_date.data and field.data and field.data < form.start_date.data:
        raise ValidationError('終了日は開始日より後に設定してください。')

class ProjectForm(FlaskForm):
    name = StringField('プロジェクト名', validators=[DataRequired(), Length(max=150)])
    description = TextAreaField('説明', validators=[Optional()])
    start_date = DateField('開始日', format='%Y-%m-%d', validators=[DataRequired()], widget=DateInput())
    end_date = DateField('終了日', format='%Y-%m-%d', validators=[Optional(), validate_end_date_after_start])
    status = SelectField('ステータス', choices=[('未開始', '未開始'), ('進行中', '進行中'), ('完了', '完了'), ('中断', '中断')], validators=[DataRequired()])
    submit = SubmitField('登録')

    # プロジェクト名が重複していないか確認するカスタムバリデーター
    def validate_name(self, field):
        # 現在編集中のプロジェクトIDがある場合は、そのプロジェクトは除外して重複チェックを行う
        # これは編集フォームで既存のプロジェクト名を変えずに送信した場合にエラーにならないようにするため
        from models.project import Project
        query = Project.query.filter_by(name=field.data)
        if self.project_id.data: # 編集モードの場合
            query = query.filter(Project.id != self.project_id.data)
        if query.first():
            raise ValidationError('このプロジェクト名は既に登録されています。')

    # 編集フォームの場合にのみ使用される隠しフィールド
    project_id = IntegerField(validators=[Optional()]) # 編集時に使用