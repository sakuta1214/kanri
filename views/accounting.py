from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.transaction import Transaction # Transactionモデルをインポート
from models.user import db, User # dbインスタンスとUserモデルをインポート
from forms.transaction_form import TransactionForm
import datetime
from sqlalchemy import func
from views.auth import login_required # ここを修正/追加

# Blueprintを定義し、url_prefixを設定
accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')

# 取引一覧表示
@accounting_bp.route('/')
@login_required
def transaction_list():
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc()).all()

    # 総収入と総支出の計算
    total_income = db.session.query(func.sum(Transaction.amount)).filter_by(type='収入').scalar() or 0
    total_expense = db.session.query(func.sum(Transaction.amount)).filter_by(type='支出').scalar() or 0
    balance = total_income - total_expense

    user = User.query.get(session['user_id'])
    return render_template('accounting/transaction_list.html',
                            transactions=transactions,
                            total_income=total_income,
                            total_expense=total_expense,
                            balance=balance,
                            user=user)

# 取引追加
@accounting_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        new_transaction = Transaction(
            transaction_date=form.transaction_date.data,
            type=form.type.data,
            category=form.category.data,
            amount=form.amount.data,
            description=form.description.data,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        try:
            db.session.add(new_transaction)
            db.session.commit()
            flash('取引が追加されました。', 'success')
            return redirect(url_for('accounting.transaction_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'取引の追加中にエラーが発生しました: {e}', 'danger')

    user = User.query.get(session['user_id'])
    return render_template('accounting/transaction_form.html', form=form, title='取引追加', user=user)

# 取引編集
@accounting_bp.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    form = TransactionForm(obj=transaction) # 既存のデータでフォームを初期化

    if form.validate_on_submit():
        try:
            form.populate_obj(transaction) # フォームのデータでオブジェクトを更新
            transaction.updated_at = datetime.datetime.now() # 更新日時を更新
            db.session.commit()
            flash('取引情報が更新されました。', 'success')
            return redirect(url_for('accounting.transaction_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'取引情報の更新中にエラーが発生しました: {e}', 'danger')

    user = User.query.get(session['user_id'])
    return render_template('accounting/transaction_form.html', form=form, title='取引編集', user=user)

# 取引削除
@accounting_bp.route('/delete/<int:transaction_id>', methods=['POST']) # POSTメソッドのみ許可
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('取引が削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'取引の削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('accounting.transaction_list'))