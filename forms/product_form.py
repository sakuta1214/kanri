# forms/product_form.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError

class ProductForm(FlaskForm):
    name = StringField('商品名', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('商品説明', validators=[Optional()])
    price = FloatField('価格', validators=[DataRequired(), NumberRange(min=0.0, message='価格は0以上である必要があります。')])
    stock_quantity = IntegerField('在庫数量', validators=[DataRequired(), NumberRange(min=0, message='在庫数量は0以上である必要があります。')])
    submit = SubmitField('登録')

    # 商品名が重複していないか確認するカスタムバリデーター
    def validate_name(self, field):
        # 現在編集中の商品IDがある場合は、その商品は除外して重複チェックを行う
        # これは編集フォームで既存の商品名を変えずに送信した場合にエラーにならないようにするため
        from models.product import Product
        query = Product.query.filter_by(name=field.data)
        if self.product_id.data: # 編集モードの場合
            query = query.filter(Product.id != self.product_id.data)
        if query.first():
            raise ValidationError('この商品名は既に登録されています。')

    # 編集フォームの場合にのみ使用される隠しフィールド
    # views/product.pyでform.product_id.dataに値を設定する必要がある
    product_id = IntegerField(validators=[Optional()]) # 編集時に使用