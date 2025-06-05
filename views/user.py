# views/user.py
from flask import Blueprint, render_template, request, flash, url_for, redirect, session
from sqlalchemy import or_ # 複数の条件で検索するために必要
from models.user import User, db # Userモデルとdbをインポート
from views.auth import login_required # 認証デコレータをインポート

# forms.user_form から UserSearchForm をインポート
from forms.user_form import UserSearchForm, RegistrationForm # RegistrationFormは編集/削除用フォームとして仮でインポート

user_bp = Blueprint('user', __name__, url_prefix='/users')

# 従業員一覧表示
@user_bp.route('/')
@login_required
def user_list():
    logged_in_user = User.query.get(session['user_id'])
    
    # UserSearchFormのインスタンスを作成
    search_form = UserSearchForm(request.args) # GETリクエストのクエリパラメータでフォームを初期化

    # ベースとなるクエリ
    users_query = User.query

    # 検索キーワードによるフィルタリング
    if search_form.search_query.data:
        search_term = f"%{search_form.search_query.data}%"
        users_query = users_query.filter(
            or_(
                User.username.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    # ユーザー名でソートして結果を取得
    users = users_query.order_by(User.username.asc()).all()

    # 削除フォームなどのCSRFトークン用に、任意のフォームインスタンスを 'form' として渡す
    form = RegistrationForm() # ユーザー管理に特化したダミーフォーム

    return render_template(
        'user/user_list.html',
        users=users,
        user=logged_in_user,
        search_form=search_form, # 検索フォームをテンプレートに渡す
        form=form # 削除フォームのCSRFトークン用
    )

# 従業員追加 (例: 管理者のみ)
@user_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    form = RegistrationForm() # 新規ユーザー登録フォーム
    if form.validate_on_submit():
        # ユーザー名またはメールアドレスが既に存在するかチェック
        existing_user_by_username = User.query.filter_by(username=form.username.data).first()
        existing_user_by_email = User.query.filter_by(email=form.email.data).first()

        if existing_user_by_username:
            flash('そのユーザー名は既に使用されています。', 'danger')
        elif existing_user_by_email:
            flash('そのメールアドレスは既に使用されています。', 'danger')
        else:
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password
            )
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('新しい従業員が追加されました。', 'success')
                return redirect(url_for('user.user_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'従業員追加中にエラーが発生しました: {e}', 'danger')
    
    logged_in_user = User.query.get(session['user_id'])
    return render_template('user/add_user.html', form=form, title='従業員追加', user=logged_in_user)

# 従業員編集 (例: 管理者のみ)
@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user_to_edit = User.query.get_or_404(user_id)
    # ユーザー編集用のフォーム（ここではRegistrationFormを流用するが、EditUserFormを別途作成することを推奨）
    form = RegistrationForm(obj=user_to_edit) 

    # パスワードフィールドは編集時に空で表示されるため、バリデーションを調整するか、
    # 別のフォームクラス（PasswordはOptional）を用意する
    if request.method == 'POST' and form.validate_on_submit():
        try:
            user_to_edit.username = form.username.data
            user_to_edit.email = form.email.data
            # パスワードが入力された場合のみ更新
            if form.password.data:
                user_to_edit.password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            db.session.commit()
            flash('従業員情報が更新されました。', 'success')
            return redirect(url_for('user.user_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'従業員情報更新中にエラーが発生しました: {e}', 'danger')
    elif request.method == 'GET':
        # GETリクエストの場合、パスワードフィールドをクリア
        form.password.data = ''
        form.confirm_password.data = ''
    
    logged_in_user = User.query.get(session['user_id'])
    return render_template('user/edit_user.html', form=form, title='従業員編集', user=logged_in_user, user_to_edit=user_to_edit)


# 従業員削除 (例: 管理者のみ)
@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user_to_delete = User.query.get_or_404(user_id)
    # ログイン中のユーザー自身を削除しようとしていないかチェック
    if user_to_delete.id == session['user_id']:
        flash('自分自身のアカウントは削除できません。', 'danger')
        return redirect(url_for('user.user_list'))

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('従業員が削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'従業員削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('user.user_list'))

# パスワードハッシュ化のためにインポートが必要
from werkzeug.security import generate_password_hash