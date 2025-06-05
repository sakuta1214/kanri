# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
import config
from models import db, User
from views.auth import auth_bp, login_required, admin_required

# 各Blueprintをインポート
from views.employee import employee_bp
from views.customer import customer_bp
from views.product import product_bp
from views.task import task_bp
from views.schedule import schedule_bp
from views.accounting import accounting_bp
from views.project import project_bp
from views.document import document_bp
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect # ★この行のコメントアウトを解除★
from views.user import user_bp  

app = Flask(__name__)
app.config.from_object(config.Config)
db.init_app(app)
bootstrap = Bootstrap(app)
csrf = CSRFProtect(app) # ★この行のコメントアウトを解除★

# 各Blueprintを登録
app.register_blueprint(employee_bp)
app.register_blueprint(customer_bp)
app.register_blueprint(product_bp)
app.register_blueprint(task_bp)
app.register_blueprint(schedule_bp)
app.register_blueprint(accounting_bp)
app.register_blueprint(project_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(document_bp)
app.register_blueprint(user_bp) 

# アプリケーションコンテキスト内でデータベーステーブルを作成
with app.app_context():
    db.create_all()

# ルートURLはログインページへリダイレクト
@app.route('/')
def index():
    return redirect(url_for('auth.login'))

# ダッシュボード（メニュー画面）
@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    menu_items = [
        {'name': '従業員管理', 'url': url_for('employee.employee_list'), 'icon': 'users'},
        {'name': '顧客管理', 'url': url_for('customer.customer_list'), 'icon': 'address-book'},
        {'name': '在庫管理', 'url': url_for('product.product_list'), 'icon': 'boxes'},
        {'name': 'タスク管理', 'url': url_for('task.task_list'), 'icon': 'tasks'},
        {'name': 'スケジュール管理 (リスト)', 'url': url_for('schedule.schedule_list'), 'icon': 'calendar-alt'},
        {'name': 'スケジュール管理 (カレンダー)', 'url': url_for('schedule.schedule_calendar'), 'icon': 'calendar'},
        {'name': '会計・経理管理', 'url': url_for('accounting.transaction_list'), 'icon': 'chart-pie'},
        {'name': 'プロジェクト管理', 'url': url_for('project.project_list'), 'icon': 'project-diagram'},
        {'name': 'アクセス・権限管理', 'url': url_for('auth.user_list'), 'icon': 'user-lock', 'admin_only': True},
        {'name': 'ドキュメント管理', 'url': url_for('document.list_documents'), 'icon': 'file-alt'},
    ]
    return render_template('dashboard.html', menu_items=menu_items, user=user)

if __name__ == '__main__':
    app.run(debug=True)