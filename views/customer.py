# views/customer.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.customer import Customer # Customerモデルをインポート
from models.user import db, User # dbインスタンスとUserモデルをインポート
from forms.customer_form import CustomerForm
from functools import wraps

# Blueprintを定義し、url_prefixを設定
customer_bp = Blueprint('customer', __name__, url_prefix='/customers')

# ログイン必須デコレータ (views/employee.py からコピーしています)
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインしてください。', 'warning')
            return redirect(url_for('login', next=request.url))
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('ユーザーが見つかりません。再ログインしてください。', 'danger')
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 顧客一覧表示
@customer_bp.route('/')
@login_required
def customer_list():
    customers = Customer.query.all()
    user = User.query.get(session['user_id']) # base.htmlでuser情報を使えるように渡す
    return render_template('customer/customer_list.html', customers=customers, user=user)

# 顧客追加
@customer_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = CustomerForm()
    if form.validate_on_submit():
        new_customer = Customer(
            name=form.name.data,
            email=form.email.data,
            phone=form.phone.data,
            address=form.address.data,
            company=form.company.data
        )
        db.session.add(new_customer)
        db.session.commit()
        flash('顧客が追加されました。', 'success')
        return redirect(url_for('customer.customer_list'))
    user = User.query.get(session['user_id']) # base.htmlでuser情報を使えるように渡す
    return render_template('customer/customer_form.html', form=form, title='顧客追加', user=user)

# 顧客編集
@customer_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    form = CustomerForm(obj=customer) # 既存のデータでフォームを初期化

    if form.validate_on_submit():
        form.populate_obj(customer) # フォームのデータでオブジェクトを更新
        db.session.commit()
        flash('顧客情報が更新されました。', 'success')
        return redirect(url_for('customer.customer_list'))
    user = User.query.get(session['user_id']) # base.htmlでuser情報を使えるように渡す
    return render_template('customer/customer_form.html', form=form, title='顧客編集', user=user)

# 顧客削除
@customer_bp.route('/delete/<int:customer_id>', methods=['POST']) # POSTメソッドのみ許可
@login_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('顧客が削除されました。', 'danger')
    return redirect(url_for('customer.customer_list'))