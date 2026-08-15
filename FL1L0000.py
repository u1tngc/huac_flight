#PGM-ID:FL1L0000
#PGM-NAME:FLフライト管理オンラインメイン
#最終更新日:2026/08/14

from datetime import timedelta
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import os
from zoneinfo import ZoneInfo
from urllib.parse import quote

import FL1S0001
import FL1S0002
import FL1S0003

app = Flask(__name__)
app.secret_key = "your_fixed_secret_key_here"  # 固定のキーを使用
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # セッション有効期限30分

# ログインページ
@app.route('/', methods=['GET', 'POST'])
def FL_login():
    if request.method == 'POST':
        now = datetime.now(ZoneInfo("Asia/Tokyo"))
        if now.weekday() in [1] and now.hour == 0 and now.minute < 30:
            flash("日曜の午前0時から午前0時30分まではメンテナンス時間です。")
            return redirect(url_for('FL_login'))
        in_password = request.form['password']
        in_user = request.form['user']
        # if in_user not in ['16A3184', '99A0104'] :
        #     flash("現在、アップデート作業中のため、ログインできません。")
        #     return redirect(url_for('FL_login'))
        login_ret, info = FL1S0002.login_check(in_user, in_password)
        if login_ret == 0:
            session.permanent = True
            session['logged_in'] = True
            session['user_id'] = in_user
            session['authority'] = info
            return redirect(url_for('FL_menu01'))
        else:
            return 'ログイン失敗。ユーザー名またはパスワードが違います。'
    return render_template('FL_login.html')

@app.route('/FL_menu01', methods=['GET', 'POST'])
def FL_menu01():
    if not session.get('user_id'):
        return redirect(url_for('FL_login'))
    user_id = session.get('user_id')  # ユーザーIDを取得
    authority = session.get('authority')  # 権限を取得
    if request.method == 'POST':
        session_clear(user_id)
        shorikbn = request.form['selection']
        if shorikbn == "db_show":
            dbkbn = request.form["db_kbn1"]
            if dbkbn == "1":
                #機能：緊急課目履歴照会(A001)
                gakuseiName = FL1S0001.get_gakuseiInfo01()
                session[f"{user_id}_gakuseiName_A001"] = gakuseiName
                return render_template('FL_db021.html', gakuseiName=gakuseiName)
        elif shorikbn == "db_edit":
            dbkbn = request.form["db_kbn2"]
            if dbkbn == "0":
                #機能：通常課目履歴登録(B000)
                if session.get(f"authority") in [0,1]:
                    session[f"{user_id}_gakuseiID_B000"] = user_id
                    return redirect(url_for('FL_db065'))
                else:
                    gakuseiName = FL1S0001.get_gakuseiInfo01()
                    session[f"{user_id}_gakuseiName_B000"] = gakuseiName
                    return render_template('FL_db063.html', gakuseiName=gakuseiName)
            elif dbkbn == "1":
                #機能：緊急課目登録(B001)
                gakuseiName = FL1S0001.get_gakuseiInfo01()
                session[f"{user_id}_gakuseiName_B001"] = gakuseiName
                return render_template('FL_db023.html', gakuseiName=gakuseiName)
        elif shorikbn == "user_edit":
            dbkbn = request.form["db_kbn3"]
            if dbkbn == "0":
                #機能：ユーザー情報照会(C000)
                userList = FL1S0002.get_userAll()
                return render_template('FL_db001.html',userList=userList)     
            elif dbkbn == "1":
                #機能：ユーザー情報訂正(C001)
                userData = FL1S0002.get_user01()
                session[f"{user_id}_userData_C001"] = userData
                return render_template('FL_db002.html', userData=userData, err1="")
            if dbkbn == "2":
                #機能：ユーザー情報登録(C002)
                return redirect(url_for('FL_db004',err=""))
        elif shorikbn == "kinkyu_rireki":
            #機能：緊急課目状況一括照会(D001)
            kinkyuList = FL1S0001.get_kinkyu_rireki()
            return render_template('FL_db041.html', kinkyuList=kinkyuList)
        elif shorikbn == "SoloChk":
            #機能：単座チェック(D002)
            if authority not in [0]:
                gakuseiName = FL1S0001.get_gakuseiInfo01()
                session[f"{user_id}_gakuseiName_D002"] = gakuseiName
                return render_template('FL_db051.html', gakuseiName=gakuseiName)
            else:
                name ,rireki0, rireki1, rireki2,rireki3 = FL1S0001.get_SoloChk(user_id)
                session[f'{user_id}_gakuseiID_D002'] = user_id
                session[f'{user_id}_rireki0_D002'] = rireki0
                session[f'{user_id}_rireki1_D002'] = rireki1
                session[f'{user_id}_rireki2_D002'] = rireki2
                session[f'{user_id}_rireki3_D002'] = rireki3
                session[f'{user_id}_name_D002'] = name
                return redirect(url_for('FL_db052'))
        elif shorikbn == "password":
            #機能：パスワード変更
            return redirect(url_for('FL_db010',err=""))
    return render_template('FL_menu01.html')

#ユーザー管理セグ・照会
@app.route('/FL_db001', methods=['GET', 'POST'])
def FL_db001():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('GK_login'))
    if not session.get('authority') in [1,5,8,9]:
        return redirect(url_for('FL_menu01'))
    return render_template('FL_db001.html')

#パスワード変更
@app.route('/FL_db010', methods=['GET', 'POST'])
def FL_db010():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if request.method == 'POST':
        pass1 = request.form['pass1']
        pass2 = request.form['pass2']
        err = FL1S0002.check03(pass1, pass2)
        if err:
            return render_template('FL_db010.html', err =err)
        err = FL1S0002.update_password(user_id,pass1)
        flash(f"{user_id}のパスワード変更が完了しました。")
        return redirect(url_for('FL_menu01'))
    return render_template('FL_db010.html', err ="")

#緊急課目履歴照会１
@app.route('/FL_db021', methods=['GET', 'POST'])
def FL_db021():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiName_A001" not in session:
        return redirect(url_for('FL_menu01'))
    if request.method == 'POST':
        gakuseiID = request.form['selected_student']
        session[f'{user_id}_gakuseiID_A001'] = gakuseiID
        rireki = FL1S0001.get_rireki(gakuseiID,[1, 2])
        session[f'{user_id}_rireki_A001'] = rireki
        return redirect(url_for('FL_db022'))
    return render_template('FL_db021.html', gakuseiName=session.get(f"{user_id}_gakuseiName_A001"))

#緊急課目履歴照会２
@app.route('/FL_db022', methods=['GET', 'POST'])
def FL_db022():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiID_A001" not in session:
        return redirect(url_for('FL_menu01'))
    if request.method == 'POST':
        return redirect(url_for('FL_menu01'))
    rireki = session.get(f'{user_id}_rireki_A001')
    #履歴0件でも氏名を表示できるよう、学籍番号から氏名を取得する
    gakuseiName = FL1S0001.get_gakuseiName(session.get(f'{user_id}_gakuseiID_A001'))

    return render_template('FL_db022.html', rireki=rireki, gakuseiName=gakuseiName)

#通常課目履歴更新（学生選択）
@app.route('/FL_db063', methods=['GET', 'POST'])
def FL_db063():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiName_B000" not in session:
        return redirect(url_for('FL_menu01'))
    if request.method == 'POST':
        gakuseiID = request.form['selected_student']
        session[f'{user_id}_gakuseiID_B000'] = gakuseiID
        return redirect(url_for('FL_db064'))
    return render_template('FL_db063.html', gakuseiName=session.get(f"{user_id}_gakuseiName_B000"))

#通常課目実施履歴更新（登録・訂正）
@app.route('/FL_db064', methods=['GET', 'POST'])
def FL_db064():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiID_B000" not in session:
        return redirect(url_for('FL_menu01'))
    gakuseiID = session.get(f'{user_id}_gakuseiID_B000')
    if request.method == 'POST':
        op = request.form['op']
        if op == "insert":
            ymd = request.form['ymd'].replace('-', '')
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            comment = request.form['comment']
            err = FL1S0001.regist_rireki(gakuseiID, ymd, bangou, edaban, comment, user_id)
            if err:
                return render_template('FL_db064.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",0), kamokuList=FL1S0001.get_kamokuList(0), err=err)
            flash("登録が完了しました。")
        elif op == "update":
            ymd = request.form['ymd']
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            comment = request.form['comment']
            bunya = bangou[0:1]
            kbn = bangou[1:2]
            bangou = bangou[2:6]
            err = FL1S0001.correct_rireki(gakuseiID, ymd, bunya, kbn, bangou, edaban, comment)
            if err:
                return render_template('FL_db064.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",0), kamokuList=FL1S0001.get_kamokuList(0), err=err)
            flash("訂正が完了しました。")
        elif op == "delete":
            ymd = request.form['ymd']
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            bunya = bangou[0:1]
            kbn = bangou[1:2]
            bangou = bangou[2:6]
            err = FL1S0001.delete_rireki(gakuseiID, ymd, bunya, kbn, bangou, edaban)
            if err:
                return render_template('FL_db064.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",0), kamokuList=FL1S0001.get_kamokuList(0), err=err)
            flash("削除が完了しました。")
        return redirect(url_for('FL_db064'))
    return render_template('FL_db064.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",0), kamokuList=FL1S0001.get_kamokuList(0), err="")

#通常課目履歴更新（登録・訂正）学生用
@app.route('/FL_db065', methods=['GET', 'POST'])
def FL_db065():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiID_B000" not in session:
        return redirect(url_for('FL_menu01'))
    gakuseiID = session.get(f'{user_id}_gakuseiID_B000')
    if request.method == 'POST':
        op = request.form['op']
        if op == "insert":
            ymd = request.form['ymd'].replace('-', '')
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            kyokan = request.form['kyokan']
            comment = request.form['comment']
            err = FL1S0001.regist_rireki1(gakuseiID, ymd, bangou, edaban, kyokan, comment)
            if err:
                return render_template('FL_db065.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",3), kamokuList=FL1S0001.get_kamokuList(3), kyokanList=FL1S0001.get_kyokanList(), err=err)
            flash("登録が完了しました。")
        elif op == "update":
            ymd = request.form['ymd']
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            comment = request.form['comment']
            bunya = bangou[0:1]
            kbn = bangou[1:2]
            bangou = bangou[2:6]
            err = FL1S0001.correct_rireki(gakuseiID, ymd, bunya, kbn, bangou, edaban, comment)
            if err:
                return render_template('FL_db065.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",3), kamokuList=FL1S0001.get_kamokuList(3), kyokanList=FL1S0001.get_kyokanList(), err=err)
            flash("訂正が完了しました。")
        elif op == "delete":
            ymd = request.form['ymd']
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            bunya = bangou[0:1]
            kbn = bangou[1:2]
            bangou = bangou[2:6]
            err = FL1S0001.delete_rireki(gakuseiID, ymd, bunya, kbn, bangou, edaban)
            if err:
                return render_template('FL_db065.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",3), kamokuList=FL1S0001.get_kamokuList(3), kyokanList=FL1S0001.get_kyokanList(), err=err)
            flash("削除が完了しました。")
        return redirect(url_for('FL_db065'))
    return render_template('FL_db065.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID,"",3), kamokuList=FL1S0001.get_kamokuList(3), kyokanList=FL1S0001.get_kyokanList(), err="")

#緊急課目登録（学生選択）
@app.route('/FL_db023', methods=['GET', 'POST'])
def FL_db023():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiName_B001" not in session:
        return redirect(url_for('FL_menu01'))
    if request.method == 'POST':
        gakuseiID = request.form['selected_student']
        session[f'{user_id}_gakuseiID_B001'] = gakuseiID
        return redirect(url_for('FL_db024'))
    return render_template('FL_db023.html', gakuseiName=session.get(f"{user_id}_gakuseiName_B001"))

#緊急課目登録（登録・訂正）
@app.route('/FL_db024', methods=['GET', 'POST'])
def FL_db024():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiID_B001" not in session:
        return redirect(url_for('FL_menu01'))
    gakuseiID = session.get(f'{user_id}_gakuseiID_B001')
    if request.method == 'POST':
        op = request.form['op']
        if op == "insert":
            ymd = request.form['ymd'].replace('-', '')
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            comment = request.form['comment']
            err = FL1S0001.regist_rireki(gakuseiID, ymd, bangou, edaban, comment, user_id)
            if err:
                return render_template('FL_db024.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID, "F", [1, 2]), kamokuList=FL1S0001.get_kamokuList([1, 2]), err=err)
            flash("登録が完了しました。")
        elif op == "update":
            ymd = request.form['ymd']
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            comment = request.form['comment']
            bunya = bangou[0:1]
            kbn = bangou[1:2]
            bangou = bangou[2:6]
            err = FL1S0001.correct_rireki(gakuseiID, ymd, bunya, kbn, bangou, edaban, comment)
            if err:
                return render_template('FL_db024.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID, "F", [1, 2]), kamokuList=FL1S0001.get_kamokuList([1, 2]), err=err)
            flash("訂正が完了しました。")
        elif op == "delete":
            ymd = request.form['ymd']
            bangou = request.form['bangou']
            edaban = request.form['edaban']
            bunya = bangou[0:1]
            kbn = bangou[1:2]
            bangou = bangou[2:6]
            err = FL1S0001.delete_rireki(gakuseiID, ymd, bunya, kbn, bangou, edaban)
            if err:
                return render_template('FL_db024.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID, "F", [1, 2]), kamokuList=FL1S0001.get_kamokuList([1, 2]), err=err)
            flash("削除が完了しました。")
        return redirect(url_for('FL_db024'))
    return render_template('FL_db024.html', gakuseiName=FL1S0001.get_gakuseiName(gakuseiID), rireki=FL1S0001.get_rirekiEdit(gakuseiID, "F", [1, 2]), kamokuList=FL1S0001.get_kamokuList([1, 2]), err="")

#ユーザー管理セグ訂正・照会
@app.route('/FL_db002', methods=['GET', 'POST'])
def FL_db002():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if not session.get('authority') in [5,8,9]:
        return redirect(url_for('FL_menu01'))

    if request.method == 'POST':
        userInfo = request.form['selected_userInfo']
        session[f'{user_id}_gakuseiInfo_C001'] = userInfo
        ret_gakusei = FL1S0002.get_user02(userInfo)
        session[f'{user_id}_user_C001'] = ret_gakusei
        return redirect(url_for('FL_db003', userInfo=session.get(f'{user_id}_user_C001'), err=""))
    return render_template('FL_db002.html')

#ユーザー管理セグ・訂正
@app.route('/FL_db003', methods=['GET', 'POST'])
def FL_db003():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if not session.get('authority') in [5,8,9]:
        return redirect(url_for('FL_menu01'))

    if request.method == 'POST':
        name = request.form['name']
        status_cd = request.form['status_cd']
        err = FL1S0002.check02(name, status_cd)
        if err:
            return render_template('FL_db003.html', userInfo=session.get(f'{user_id}_user_C001'), err =err)
        list = session.get(f'{user_id}_user_C001')
        id = list[0]
        update_user = [id, name, int(status_cd)]
        err = FL1S0002.update_user(update_user)
        err = f"[{name}]の訂正が完了しました。"
        userData = FL1S0002.get_user01()
        return render_template('FL_db002.html', userData=userData, err1=err)
    return render_template('FL_db003.html', userInfo=session.get(f'{user_id}_user_C001'), err ="")

#ユーザー管理セグ・登録
@app.route('/FL_db004', methods=['GET', 'POST'])
def FL_db004():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if not session.get('authority') in [5,8,9]:
        return redirect(url_for('FL_menu01'))

    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        status_cd = int(request.form['status_cd'])
        err = FL1S0002.check04(id, name)
        if err:
            return render_template('FL_db004.html', err =err)
        err = FL1S0002.insert_user(id, name, status_cd)
        if err:
            return render_template('FL_db004.html', err =err)
        flash("ユーザーの登録が完了しました。")
        return redirect(url_for('FL_menu01'))

    return render_template('FL_db004.html', err="")

#緊急課目状況一括照会
@app.route('/FL_db041', methods=['GET', 'POST'])
def FL_db041():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    return render_template('FL_db041.html')

#単座チェック（学生選択）
@app.route('/FL_db051', methods=['GET', 'POST'])
def FL_db051():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiName_D002" not in session:
        return redirect(url_for('FL_menu01'))
    if request.method == 'POST':
        gakuseiID = request.form['selected_student']
        op = request.form.get('op', 'next')
        if op == "excel":
            return FL1S0003.make_SoloChk_excelResponse()
        else:
            session[f'{user_id}_gakuseiID_D002'] = gakuseiID
            name ,rireki0, rireki1, rireki2,rireki3 = FL1S0001.get_SoloChk(gakuseiID)
            session[f'{user_id}_rireki0_D002'] = rireki0
            session[f'{user_id}_rireki1_D002'] = rireki1
            session[f'{user_id}_rireki2_D002'] = rireki2
            session[f'{user_id}_rireki3_D002'] = rireki3
            session[f'{user_id}_name_D002'] = name
            print(rireki1[6])
            print(rireki2[5])
            print(rireki3[4])
            return redirect(url_for('FL_db052'))
    return render_template('FL_db051.html', gakuseiName=session.get(f"{user_id}_gakuseiName_D002"))

#単座チェック（チェック画面）
@app.route('/FL_db052', methods=['GET', 'POST'])
def FL_db052():
    user_id = session.get('user_id')
    if not session.get('logged_in'):
        return redirect(url_for('FL_login'))
    if f"{user_id}_gakuseiID_D002" not in session:
        return redirect(url_for('FL_menu01'))
    if request.method == 'POST':
        return redirect(url_for('FL_menu01'))
    return render_template('FL_db052.html', gakuseiName=session.get(f"{user_id}_name_D002"), rireki0=session.get(f'{user_id}_rireki0_D002'), rireki1=session.get(f'{user_id}_rireki1_D002'), rireki2=session.get(f'{user_id}_rireki2_D002'), rireki3=session.get(f'{user_id}_rireki3_D002'))

# セッションの有効期限をリセット
@app.before_request
def refresh_session():
    session.modified = True  

def session_clear(user_id):
    session.pop(f"{user_id}_gakuseiName_A001", None)
    session.pop(f"{user_id}_gakuseiID_A001", None)
    session.pop(f"{user_id}_rireki_A001", None)
    session.pop(f"{user_id}_gakuseiName_B001", None)
    session.pop(f"{user_id}_gakuseiID_B001", None)
    session.pop(f"{user_id}_user_C001", None)
    session.pop(f"{user_id}_userData_C001", None)
    session.pop(f"{user_id}_gakuseiInfo_C001", None)
    session.pop(f"{user_id}_gakuseiName_D002", None)
    session.pop(f"{user_id}_gakuseiID_D002", None)
    session.pop(f"{user_id}_rireki0_D002", None)
    session.pop(f"{user_id}_rireki1_D002", None)
    session.pop(f"{user_id}_rireki2_D002", None)
    session.pop(f"{user_id}_rireki3_D002", None)

# ログアウト
@app.route('/FL_logout')
def FL_logout():
    session.clear()
    return redirect(url_for('FL_login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)