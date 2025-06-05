from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# すべてのモデルファイルから対応するクラスがインポートされていることを確認
from .user import User
from .document import Document
from .employee import Employee
from .customer import Customer
from .product import Product
from .task import Task
from .schedule import Schedule
# from .accounting import Accounting # accounting.pyが存在しない場合、この行はコメントアウトするか削除します
from .transaction import Transaction # transaction.pyにTransactionクラスがある場合
from .project import Project