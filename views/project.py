# views/project.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models.project import Project # Projectモデルをインポート
from models.user import db, User # dbインスタンスとUserモデルをインポート
from forms.project_form import ProjectForm
from functools import wraps
import datetime

# Blueprintを定義し、url_prefixを設定
project_bp = Blueprint('project', __name__, url_prefix='/projects')

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

# プロジェクト一覧表示
@project_bp.route('/')
@login_required
def project_list():
    projects = Project.query.order_by(Project.start_date.desc()).all() # 開始日でソート
    user = User.query.get(session['user_id'])
    return render_template('project/project_list.html', projects=projects, user=user)

# プロジェクト追加
@project_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_project():
    form = ProjectForm()
    # 隠しフィールドのproject_idは新規追加時には不要なので、Noneを設定
    form.project_id.data = None
    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        try:
            db.session.add(new_project)
            db.session.commit()
            flash('プロジェクトが追加されました。', 'success')
            return redirect(url_for('project.project_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'プロジェクトの追加中にエラーが発生しました: {e}', 'danger')
            if "UNIQUE constraint failed" in str(e):
                flash('このプロジェクト名は既に存在します。別の名前をお試しください。', 'danger')


    user = User.query.get(session['user_id'])
    return render_template('project/project_form.html', form=form, title='プロジェクト追加', user=user)

# プロジェクト編集
@project_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    form = ProjectForm(obj=project) # 既存のデータでフォームを初期化
    form.project_id.data = project_id # 隠しフィールドにプロジェクトIDを設定

    if form.validate_on_submit():
        try:
            form.populate_obj(project) # フォームのデータでオブジェクトを更新
            project.updated_at = datetime.datetime.now() # 更新日時を更新
            db.session.commit()
            flash('プロジェクト情報が更新されました。', 'success')
            return redirect(url_for('project.project_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'プロジェクト情報の更新中にエラーが発生しました: {e}', 'danger')
            if "UNIQUE constraint failed" in str(e):
                flash('このプロジェクト名は既に存在します。別の名前をお試しください。', 'danger')


    user = User.query.get(session['user_id'])
    return render_template('project/project_form.html', form=form, title='プロジェクト編集', user=user)

# プロジェクト削除
@project_bp.route('/delete/<int:project_id>', methods=['POST']) # POSTメソッドのみ許可
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    try:
        db.session.delete(project)
        db.session.commit()
        flash('プロジェクトが削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'プロジェクトの削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('project.project_list'))