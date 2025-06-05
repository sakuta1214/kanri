# views/document.py
import os
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app, send_from_directory
from models.document import Document
from models.user import db, User # Userモデルが使われていなくても、session['user_id']からuserオブジェクトを取得するために必要
from forms.document_form import UploadDocumentForm, EditDocumentForm
from views.auth import login_required # 認証デコレータをインポート
import datetime
from werkzeug.utils import secure_filename # ファイル名の安全化

# Blueprintの定義
document_bp = Blueprint('document', __name__, url_prefix='/document')

# ドキュメント一覧表示
@document_bp.route('/')
@login_required
def list_documents():
    """登録されているすべてのドキュメントを一覧表示します。"""
    # ここを修正: Document.uploaded_at から Document.upload_date へ
    documents = Document.query.order_by(Document.upload_date.desc()).all()
    logged_in_user = User.query.get(session['user_id'])
    # 削除フォームのCSRFトークン用に空のフォームインスタンスを渡す（推奨される方法の一つ）
    # あるいは、base.htmlでcsrf_token()関数を直接呼び出す（Flask-WTFが有効な場合）
    from forms.document_form import UploadDocumentForm # 削除フォームにCSRFトークンを渡すため
    form = UploadDocumentForm() # form.csrf_token をテンプレートで利用するため
    return render_template('document/list_documents.html', documents=documents, user=logged_in_user, form=form)

# ドキュメントアップロード
@document_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_document():
    """新しいドキュメントをアップロードする機能を提供します。"""
    form = UploadDocumentForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        file = form.file.data

        # ファイルが選択されているか確認
        if file:
            # ファイル名を安全な形式に変換
            filename = secure_filename(file.filename)
            # ファイルを保存するディレクトリが存在しない場合は作成
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            file_path = os.path.join(upload_folder, filename)
            
            try:
                # ファイルをサーバーに保存
                file.save(file_path)

                # データベースにドキュメント情報を保存
                new_document = Document(
                    title=title,
                    description=description,
                    filename=filename,
                    # ここを修正: uploaded_at から upload_date へ
                    upload_date=datetime.datetime.now() # または db.func.current_timestamp()
                    # user_id=session['user_id'] # ドキュメントをユーザーに紐付ける場合
                )
                db.session.add(new_document)
                db.session.commit()
                flash('ドキュメントが正常にアップロードされました。', 'success')
                return redirect(url_for('document.list_documents'))
            except Exception as e:
                db.session.rollback()
                # ファイル保存またはDBコミットでエラーが発生した場合、アップロードされたファイルを削除（任意）
                if os.path.exists(file_path):
                    os.remove(file_path)
                flash(f'ドキュメントのアップロード中にエラーが発生しました: {e}', 'danger')
        else:
            flash('ファイルが選択されていません。', 'warning')

    logged_in_user = User.query.get(session['user_id'])
    return render_template('document/upload_document.html', form=form, title='ドキュメントアップロード', user=logged_in_user)

# ドキュメントダウンロード
@document_bp.route('/download/<int:doc_id>')
@login_required
def download_document(doc_id):
    """指定されたIDのドキュメントファイルをダウンロードします。"""
    document = Document.query.get_or_404(doc_id)
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
        # ファイルが存在することを確認
        if os.path.exists(file_path):
            return send_from_directory(current_app.config['UPLOAD_FOLDER'], document.filename, as_attachment=True)
        else:
            flash('指定されたファイルが見つかりません。', 'danger')
            return redirect(url_for('document.list_documents'))
    except Exception as e:
        flash(f'ファイルのダウンロード中にエラーが発生しました: {e}', 'danger')
        return redirect(url_for('document.list_documents'))

# ドキュメント編集
@document_bp.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
@login_required
def edit_document(doc_id):
    """指定されたIDのドキュメント情報を編集します。"""
    document = Document.query.get_or_404(doc_id)
    form = EditDocumentForm(obj=document) # EditDocumentForm を使用

    if form.validate_on_submit():
        try:
            # タイトルと説明を更新
            document.title = form.title.data
            document.description = form.description.data

            # 新しいファイルが選択された場合
            if form.file.data:
                # 古いファイルを削除
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

                # 新しいファイルを保存
                filename = secure_filename(form.file.data.filename)
                new_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.file.data.save(new_file_path)
                document.filename = filename # データベースのファイル名も更新
                # ファイルが更新された場合、アップロード日時も更新する
                document.upload_date = datetime.datetime.now()
                
            db.session.commit()
            flash('ドキュメント情報が更新されました。', 'success')
            return redirect(url_for('document.list_documents'))
        except Exception as e:
            db.session.rollback()
            flash(f'ドキュメント情報の更新中にエラーが発生しました: {e}', 'danger')

    logged_in_user = User.query.get(session['user_id'])
    return render_template('document/edit_document.html', form=form, title='ドキュメント編集', user=logged_in_user, document_id=doc_id)

# ドキュメント削除
@document_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    """指定されたIDのドキュメントと関連ファイルを削除します。"""
    document = Document.query.get_or_404(doc_id)
    try:
        # 実際のファイルもサーバーから削除
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], document.filename)
        if os.path.exists(file_path):
            os.remove(file_path)

        # データベースからドキュメントレコードを削除
        db.session.delete(document)
        db.session.commit()
        flash('ドキュメントが削除されました。', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'ドキュメントの削除中にエラーが発生しました: {e}', 'danger')
    return redirect(url_for('document.list_documents'))