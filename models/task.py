# models/task.py
from .user import db # models/user.py で定義されたdbインスタンスをインポート
import datetime

class Task(db.Model):
    __tablename__ = 'tasks' # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False) # タスクタイトル
    description = db.Column(db.Text, nullable=True) # 詳細
    due_date = db.Column(db.Date, nullable=True) # 期限日
    status = db.Column(db.String(50), nullable=False, default='未着手') # ステータス (例: 未着手, 進行中, 完了, 保留)
    priority = db.Column(db.String(50), nullable=False, default='中') # 優先度 (例: 低, 中, 高, 緊急)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now) # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now) # 更新日時

    # 必要に応じて、担当者 (従業員) や関連顧客への外部キーを追加することもできます
    # employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    # customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=True)
    # employee = db.relationship('Employee', backref='tasks_assigned')
    # customer = db.relationship('Customer', backref='tasks_related')


    def __repr__(self):
        return f'<Task {self.title}>'