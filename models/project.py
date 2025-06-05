# models/project.py
from .user import db # models/user.py で定義されたdbインスタンスをインポート
import datetime

class Project(db.Model):
    __tablename__ = 'projects' # テーブル名を明示的に指定
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False, unique=True) # プロジェクト名 (ユニーク)
    description = db.Column(db.Text, nullable=True) # プロジェクト説明
    start_date = db.Column(db.Date, nullable=False, default=datetime.date.today) # 開始日
    end_date = db.Column(db.Date, nullable=True) # 終了日 (任意)
    status = db.Column(db.String(50), nullable=False, default='未開始') # ステータス (例: 未開始, 進行中, 完了, 中断)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now) # 作成日時
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now) # 更新日時

    def __repr__(self):
        return f'<Project {self.name}>'