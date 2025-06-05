# models/customer.py
from .user import db # models/user.py で定義されたdbインスタンスをインポート

class Customer(db.Model):
    __tablename__ = 'customers' # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False) # 顧客名
    email = db.Column(db.String(120), unique=True, nullable=True) # メールアドレス (任意、ユニーク)
    phone = db.Column(db.String(20), nullable=True) # 電話番号
    address = db.Column(db.String(200), nullable=True) # 住所
    company = db.Column(db.String(100), nullable=True) # 所属会社

    def __repr__(self):
        return f'<Customer {self.name}>'