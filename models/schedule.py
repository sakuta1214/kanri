# models/schedule.py
from . import db
import datetime

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    all_day = db.Column(db.Boolean, default=False, nullable=False) # ★追加されたカラム★
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # ユーザーと紐付ける場合
    # user = db.relationship('User', backref='schedules', lazy=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __repr__(self):
        return f'<Schedule {self.title}>'