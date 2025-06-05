# views/task.py
import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from sqlalchemy import or_ # or_を使ってAND条件で検索

from models.task import Task
from models.user import db, User # dbとUserモデルもインポート
from forms.task_form import TaskForm, TaskSearchForm # TaskSearchFormをインポート
from views.auth import login_required # 認証デコレータをインポート

task_bp = Blueprint('task', __name__, url_prefix='/task')

# タスク一覧表示
@task_bp.route('/')
@login_required
def task_list():
    """登録されているすべてのタスクを一覧表示し、絞り込み検索機能を提供します。"""
    logged_in_user = User.query.get(session['user_id'])
    
    # TaskSearchFormのインスタンスを作成し、GETリクエストのクエリパラメータで初期化
    search_form = TaskSearchForm(request.args)

    # ベースとなるクエリ
    tasks_query = Task.query

    # 検索キーワードによるフィルタリング
    if search_form.search_query.data:
        search_term = f"%{search_form.search_query.data}%"
        tasks_query = tasks_query.filter(
            or_(
                Task.title.ilike(search_term),
                Task.description.ilike(search_term)
            )
        )

    # ステータスによるフィルタリング
    # 'すべて' が選択された場合（空文字列）、フィルタリングを行わない
    if search_form.status_filter.data:
        tasks_query = tasks_query.filter_by(status=search_form.status_filter.data)

    # 期日順にソートして結果を取得
    tasks = tasks_query.order_by(Task.due_date.asc()).all()

    # 削除フォームのCSRFトークン用に、任意のフォームインスタンスを 'form' としてテンプレートに渡す
    form = TaskForm() 

    return render_template(
        'task/task_list.html',
        tasks=tasks,
        user=logged_in_user,
        search_form=search_form, # 検索フォームをテンプレートに渡す
        form=form # 削除フォームのCSRFトークン用
    )

# タスク追加
@task_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    """新しいタスクを追加する機能を提供します。"""
    form = TaskForm()
    if form.validate_on_submit():
        new_task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status=form.status.data, # statusフィールドがフォームにある場合
            created_by=session['user_id'] # タスク作成者を記録する場合
        )
        try:
            db.session.add(new_task)
            db.session.commit()
            flash('タスクが正常に追加されました。', 'success')
            return redirect(url_for('task.task_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'タスクの追加中にエラーが発生しました: {e}', 'danger')
    
    logged_in_user = User.query.get(session['user_id'])
    return render_template('task/add_task.html', form=form, title='タスク追加', user=logged_in_user)

# タスク編集
@task_bp.route('/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    """指定されたIDのタスク情報を編集します。"""
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task) # obj=taskで既存データをフォームにプリフィル

    if form.validate_on_submit():
        try:
            task.title = form.title.data
            task.description = form.description.data
            task.due_date = form.due_date.data
            task.status = form.status.data # statusフィールドがフォームにある場合
            db.session.commit()
            flash('タスクが正常に更新されました。', 'success')
            return redirect(url_for('task.task_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'タスクの更新中にエラーが発生しました: {e}', 'danger')
    
    logged_in_user = User.query.get(session['user_id'])
    return render_template('task/edit_task.html', form=form, title='タスク編集', user=logged_in_user)

# タスク削除
@task_bp.route('/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    """指定されたIDのタスクを削除します。"""
    task = Task.query.get_or_404(task_id)
    try:
        db.session.delete(task)
        db.session.commit()
        flash('タスクが正常に削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'タスクの削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('task.task_list'))