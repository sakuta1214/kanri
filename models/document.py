# models/document.py
from . import db
import datetime

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    # Check this line: Is it 'uploaded_at' or 'upload_date' or something else?
    upload_date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False) # <--- This is likely 'upload_date'
    # uploaded_at = db.Column(db.DateTime, default=db.func.current_timestamp()) # <--- If it was this, the error wouldn't happen

    def __repr__(self):
        return f'<Document {self.title}>'