from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.user import User, db
from forms.auth_form import RegisterForm, LoginForm, EditUserForm # EditUserFormをインポート
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime

auth_bp = Blueprint('auth', __name__)

# ログイン必須デコレータ
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインしてください。', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        user = User.query.get(session['user_id'])
        if not user:
            session.pop('user_id', None)
            flash('ユーザーが見つかりません。再ログインしてください。', 'danger')
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# 管理者権限必須デコレータ
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('ログインしてください。', 'warning')
            return redirect(url_for('auth.login', next=request.url))
        user = User.query.get(session['user_id'])
        if not user or user.role != '管理者': # '管理者'ロールであることを確認
            flash('管理者権限が必要です。', 'danger')
            return redirect(url_for('dashboard')) # 管理者以外はダッシュボードへリダイレクト
        return f(*args, **kwargs)
    return decorated_function

# ログイン機能
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data): # モデルの check_password メソッドを使用
            session['user_id'] = user.id
            session['username'] = user.username # セッションにユーザー名を保存
            session['user_role'] = user.role # セッションにユーザーロールを保存
            flash('ログインしました。', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        else:
            flash('無効なユーザー名またはパスワードです。', 'danger')
    return render_template('auth/login.html', form=form)

# ログアウト機能
@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('user_role', None) # セッションからユーザーロールを削除
    flash('ログアウトしました。', 'info')
    return redirect(url_for('auth.login'))


# ユーザー登録機能
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        new_user.set_password(form.password.data) # この行でパスワードが設定されます

        try:
            db.session.add(new_user)
            db.session.commit()
            flash('ユーザー登録が完了しました！', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'ユーザー登録中にエラーが発生しました: {e}', 'danger')
            # UNIQUE constraint failed エラーのハンドリングも残しておく
            if "UNIQUE constraint failed" in str(e):
                flash('このユーザー名またはメールアドレスは既に登録されています。', 'danger')

    return render_template('auth/register.html', form=form)


# --- ユーザー管理機能（管理者用） ---

# ユーザー一覧表示
@auth_bp.route('/users')
@admin_required # 管理者のみアクセス可能
def user_list():
    users = User.query.order_by(User.created_at.asc()).all()
    logged_in_user = User.query.get(session['user_id'])
    return render_template('auth/user_list.html', users=users, user=logged_in_user)

# ユーザー編集
@auth_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_required # 管理者のみアクセス可能
def edit_user(user_id):
    user_to_edit = User.query.get_or_404(user_id)
    form = EditUserForm(obj=user_to_edit)
    form.user_id.data = user_id # フォームの隠しフィールドにIDをセット

    if form.validate_on_submit():
        try:
            # パスワードはここでは変更しない
            user_to_edit.username = form.username.data
            user_to_edit.email = form.email.data
            user_to_edit.role = form.role.data # ロールを更新
            user_to_edit.updated_at = datetime.datetime.now()
            db.session.commit()
            flash('ユーザー情報が更新されました。', 'success')
            return redirect(url_for('auth.user_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'ユーザー情報の更新中にエラーが発生しました: {e}', 'danger')

    logged_in_user = User.query.get(session['user_id'])
    return render_template('auth/user_form.html', form=form, title='ユーザー編集', user=logged_in_user)

# ユーザー削除
@auth_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@admin_required # 管理者のみアクセス可能
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    # ログイン中のユーザー自身を削除しようとしていないかチェック
    if user_to_delete.id == session['user_id']:
        flash('自分自身のアカウントを削除することはできません。', 'danger')
        return redirect(url_for('auth.user_list'))

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash(f'ユーザー "{user_to_delete.username}" が削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'ユーザーの削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('auth.user_list'))