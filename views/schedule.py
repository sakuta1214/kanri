# views/schedule.py
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from models.schedule import Schedule # Scheduleモデルをインポート
from models.user import db, User # dbインスタンスとUserモデルをインポート
from forms.schedule_form import ScheduleForm
from views.auth import login_required # 認証デコレータをインポート
import datetime
from sqlalchemy import or_ # 検索機能用

schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# スケジュール一覧表示 (既存のリスト表示)
@schedule_bp.route('/')
@login_required
def schedule_list():
    # 検索機能 (もしあれば)
    search_query = request.args.get('q', '')
    schedules_query = Schedule.query

    if search_query:
        schedules_query = schedules_query.filter(
            or_(
                Schedule.title.ilike(f'%{search_query}%'),
                Schedule.description.ilike(f'%{search_query}%')
            )
        )
    schedules = schedules_query.order_by(Schedule.start_time.desc()).all()

    logged_in_user = User.query.get(session['user_id'])
    return render_template('schedule/schedule_list.html',
                           schedules=schedules,
                           user=logged_in_user,
                           search_query=search_query)

# --- カレンダー機能の追加部分 ---

# カレンダー表示
@schedule_bp.route('/calendar')
@login_required
def schedule_calendar():
    logged_in_user = User.query.get(session['user_id'])
    return render_template('schedule/schedule_calendar.html', user=logged_in_user)

# カレンダー用のイベントデータをJSONで返すAPIエンドポイント
@schedule_bp.route('/get_events')
@login_required
def get_events():
    # 全てのスケジュールを取得する場合
    schedules = Schedule.query.all()

    events = []
    for schedule in schedules:
        event = {
            'id': schedule.id,
            'title': schedule.title,
            'start': schedule.start_time.isoformat(), # ISO 8601 形式
            'end': schedule.end_time.isoformat() if schedule.end_time else None, # 終了時刻がない場合はNone
            'description': schedule.description,
            'allDay': schedule.all_day # all_dayカラムを使用
        }
        # FullCalendarの終日イベントは'end'の日付を含まないので、調整が必要な場合がある
        # 例: 2023-10-01 終日イベントの場合、endを2023-10-02に設定
        if schedule.all_day and schedule.end_time:
            # 終日イベントの場合、FullCalendarのendは排他的なので1日加算
            event['end'] = (schedule.end_time + datetime.timedelta(days=1)).isoformat()

        events.append(event)
    return jsonify(events)

# イベントのドラッグ&ドロップ/リサイズでデータベースを更新するためのエンドポイント
@schedule_bp.route('/update_event_time', methods=['POST'])
@login_required
def update_event_time():
    data = request.get_json()
    event_id = data.get('id')
    new_start_time_str = data.get('start_time')
    new_end_time_str = data.get('end_time') # 終日イベントの場合、endは次の日の00:00になる

    schedule = Schedule.query.get(event_id)
    if not schedule:
        return jsonify({'success': False, 'message': 'スケジュールが見つかりません'}), 404

    try:
        # ISO 8601 形式の文字列をdatetimeオブジェクトに変換
        # UTCタイムゾーンを示す 'Z' を '+00:00' に置き換えることで fromisoformat() が対応
        schedule.start_time = datetime.datetime.fromisoformat(new_start_time_str.replace('Z', '+00:00'))

        if new_end_time_str:
            schedule.end_time = datetime.datetime.fromisoformat(new_end_time_str.replace('Z', '+00:00'))
        else:
            # 終了時刻がない場合は開始時刻と同じにするか、既存の値を維持
            # FullCalendarの終日イベントのリサイズではendが提供されるので、通常はnew_end_time_strがあるはず
            schedule.end_time = schedule.start_time

        # 終日イベントの判定（ドラッグ後のデータで再評価）
        # FullCalendarが終日イベントとして扱う場合、start/endの時刻部分は00:00になることが多い
        # ただし、FullCalendar側がallDay: trueを送信してくれるとは限らないため、日付のみで判断するロジックも考慮
        if schedule.end_time and schedule.start_time.date() == (schedule.end_time - datetime.timedelta(days=1)).date():
             schedule.all_day = True
        else:
             schedule.all_day = False # 時刻が含まれる場合は終日ではないと判断

        schedule.updated_at = datetime.datetime.now()
        db.session.commit()
        return jsonify({'success': True, 'message': 'スケジュール時刻が更新されました'})
    except Exception as e:
        db.session.rollback()
        # ロギングの追加を推奨
        print(f"Error updating schedule time: {e}")
        return jsonify({'success': False, 'message': f'更新エラー: {e}'}), 500

# --- 既存のスケジュール管理関数 ---

# スケジュール追加
@schedule_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_schedule():
    form = ScheduleForm()
    if form.validate_on_submit():
        new_schedule = Schedule(
            title=form.title.data,
            description=form.description.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data if form.end_time.data else form.start_time.data, # 終了時間がなければ開始時間を使用
            all_day=form.all_day.data, # all_day フィールドを使用
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
            # user_id=session['user_id'] # ユーザーと紐付ける場合
        )
        try:
            db.session.add(new_schedule)
            db.session.commit()
            flash('スケジュールが追加されました。', 'success')
            return redirect(url_for('schedule.schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'スケジュールの追加中にエラーが発生しました: {e}', 'danger')

    logged_in_user = User.query.get(session['user_id'])
    # 日付クリックでフォームに初期値を設定するための処理
    initial_date = request.args.get('date')
    if initial_date:
        # 例: 'YYYY-MM-DD' 形式から datetime オブジェクトに変換
        # フォームのフィールドがdatetimeオブジェクトを期待する場合は変換が必要
        try:
            # 終日イベントとしてその日の00:00に設定
            form.start_time.data = datetime.datetime.strptime(initial_date + 'T00:00', '%Y-%m-%dT%H:%M')
            form.all_day.data = True # 終日イベントとしてマーク
        except ValueError:
            pass # 変換に失敗しても何もしない

    return render_template('schedule/schedule_form.html', form=form, title='スケジュール追加', user=logged_in_user)

# スケジュール編集
@schedule_bp.route('/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
def edit_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    form = ScheduleForm(obj=schedule)

    if form.validate_on_submit():
        try:
            form.populate_obj(schedule)
            schedule.updated_at = datetime.datetime.now()
            # all_day フィールドを考慮
            schedule.all_day = form.all_day.data
            db.session.commit()
            flash('スケジュール情報が更新されました。', 'success')
            return redirect(url_for('schedule.schedule_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'スケジュール情報の更新中にエラーが発生しました: {e}', 'danger')

    logged_in_user = User.query.get(session['user_id'])
    return render_template('schedule/schedule_form.html', form=form, title='スケジュール編集', user=logged_in_user)

# スケジュール削除
@schedule_bp.route('/delete/<int:schedule_id>', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    try:
        db.session.delete(schedule)
        db.session.commit()
        flash('スケジュールが削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'スケジュールの削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('schedule.schedule_list'))