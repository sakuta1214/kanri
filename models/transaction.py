# models/transaction.py
from .user import db # models/user.py で定義されたdbインスタンスをインポート
import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions' # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False, default=datetime.date.today) # 取引日
    type = db.Column(db.String(10), nullable=False) # '収入' または '支出'
    category = db.Column(db.String(100), nullable=False) # カテゴリ (例: 給与, 交通費, 食費, 売上)
    amount = db.Column(db.Float, nullable=False) # 金額
    description = db.Column(db.Text, nullable=True) # メモ、詳細
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now) # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now) # 更新日時

    def __repr__(self):
        return f'<Transaction {self.type}: {self.amount} ({self.category})>'