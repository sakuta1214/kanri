# views/employee.py
from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from models.employee import Employee # Employeeモデルをインポート
from models.user import db, User # dbインスタンスとUserモデルをインポート
from forms.employee_form import EmployeeForm
from views.auth import login_required, admin_required # 認証デコレータをインポート
import datetime
from sqlalchemy import or_ # 複数の条件で検索するために必要

employee_bp = Blueprint('employee', __name__, url_prefix='/employees')

# 従業員一覧表示
@employee_bp.route('/')
@login_required
def employee_list():
    # 検索キーワードの取得
    search_query = request.args.get('q', '') # 'q'という名前で検索キーワードを受け取る。デフォルトは空文字列。

    # クエリの初期化
    employees_query = Employee.query

    # 検索キーワードが指定されている場合、フィルタリングを適用
    if search_query:
        # 従業員名、部署、役職などで部分一致検索
        # 大文字・小文字を区別しない検索には .ilike() を使用
        employees_query = employees_query.filter(
            or_(
                Employee.full_name.ilike(f'%{search_query}%'),
                Employee.department.ilike(f'%{search_query}%'),
                Employee.position.ilike(f'%{search_query}%'),
                Employee.email.ilike(f'%{search_query}%')
            )
        )

    # ソート順序の指定 (例えば、従業員名順)
    employees = employees_query.order_by(Employee.full_name.asc()).all()

    logged_in_user = User.query.get(session['user_id'])
    return render_template('employee/employee_list.html',
                           employees=employees,
                           user=logged_in_user,
                           search_query=search_query) # 検索キーワードをテンプレートに渡す

# 従業員追加
@employee_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_employee():
    form = EmployeeForm()
    if form.validate_on_submit():
        new_employee = Employee(
            full_name=form.full_name.data,
            email=form.email.data,
            phone_number=form.phone_number.data,
            department=form.department.data,
            position=form.position.data,
            hire_date=form.hire_date.data,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        try:
            db.session.add(new_employee)
            db.session.commit()
            flash('新しい従業員が追加されました。', 'success')
            return redirect(url_for('employee.employee_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'従業員の追加中にエラーが発生しました: {e}', 'danger')
            if "UNIQUE constraint failed" in str(e):
                flash('このメールアドレスは既に登録されています。', 'danger')
    logged_in_user = User.query.get(session['user_id'])
    return render_template('employee/employee_form.html', form=form, title='従業員追加', user=logged_in_user)

# 従業員編集
@employee_bp.route('/edit/<int:employee_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    form = EmployeeForm(obj=employee) # 既存のデータでフォームを初期化

    if form.validate_on_submit():
        try:
            form.populate_obj(employee) # フォームのデータでオブジェクトを更新
            employee.updated_at = datetime.datetime.now() # 更新日時を更新
            db.session.commit()
            flash('従業員情報が更新されました。', 'success')
            return redirect(url_for('employee.employee_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'従業員情報の更新中にエラーが発生しました: {e}', 'danger')

    logged_in_user = User.query.get(session['user_id'])
    return render_template('employee/employee_form.html', form=form, title='従業員編集', user=logged_in_user)

# 従業員削除
@employee_bp.route('/delete/<int:employee_id>', methods=['POST']) # POSTメソッドのみ許可
@login_required
@admin_required
def delete_employee(employee_id):
    employee = Employee.query.get_or_404(employee_id)
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('従業員が削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'従業員の削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('employee.employee_list'))