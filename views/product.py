# views/product.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.product import Product # Productモデルをインポート
from models.user import db, User # dbインスタンスとUserモデルをインポート
from forms.product_form import ProductForm
from functools import wraps
import datetime

# Blueprintを定義し、url_prefixを設定
product_bp = Blueprint('product', __name__, url_prefix='/products')

# ログイン必須デコレータ (既存のものを流用)
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

# 製品一覧表示
@product_bp.route('/')
@login_required
def product_list():
    products = Product.query.all()
    user = User.query.get(session['user_id'])
    return render_template('product/product_list.html', products=products, user=user)

# 製品追加
@product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    form = ProductForm()
    # 隠しフィールドのproduct_idは新規追加時には不要なので、Noneを設定
    form.product_id.data = None
    if form.validate_on_submit():
        new_product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            stock_quantity=form.stock_quantity.data,
            last_updated=datetime.datetime.now() # 現在の日時をセット
        )
        try:
            db.session.add(new_product)
            db.session.commit()
            flash('商品が追加されました。', 'success')
            return redirect(url_for('product.product_list'))
        except Exception as e:
            db.session.rollback() # エラー時はロールバック
            flash(f'商品の追加中にエラーが発生しました: {e}', 'danger')
            # ユニーク制約違反など、データベースレベルのエラーもここで捕捉
            if "UNIQUE constraint failed" in str(e):
                flash('その商品名は既に存在します。別の名前をお試しください。', 'danger')


    user = User.query.get(session['user_id'])
    return render_template('product/product_form.html', form=form, title='商品追加', user=user)

# 製品編集
@product_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product) # 既存のデータでフォームを初期化
    form.product_id.data = product_id # 隠しフィールドに商品IDを設定

    if form.validate_on_submit():
        try:
            form.populate_obj(product) # フォームのデータでオブジェクトを更新
            product.last_updated = datetime.datetime.now() # 更新日時を更新
            db.session.commit()
            flash('商品情報が更新されました。', 'success')
            return redirect(url_for('product.product_list'))
        except Exception as e:
            db.session.rollback() # エラー時はロールバック
            flash(f'商品情報の更新中にエラーが発生しました: {e}', 'danger')
            if "UNIQUE constraint failed" in str(e):
                flash('その商品名は既に存在します。別の名前をお試しください。', 'danger')

    user = User.query.get(session['user_id'])
    return render_template('product/product_form.html', form=form, title='商品編集', user=user)

# 製品削除
@product_bp.route('/delete/<int:product_id>', methods=['POST']) # POSTメソッドのみ許可
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('商品が削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'商品の削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('product.product_list'))