# models/product.py
from .user import db # models/user.py で定義されたdbインスタンスをインポート
import datetime

class Product(db.Model):
    __tablename__ = 'products' # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True) # 商品名 (ユニーク)
    description = db.Column(db.Text, nullable=True) # 商品説明
    price = db.Column(db.Float, nullable=False, default=0.0) # 価格
    stock_quantity = db.Column(db.Integer, nullable=False, default=0) # 在庫数量
    last_updated = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now) # 最終更新日時

    def __repr__(self):
        return f'<Product {self.name}>'