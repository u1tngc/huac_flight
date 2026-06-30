#PGM-ID:FL1S0002
#PGM-NAME:FLフライト管理ユーザーサブ
#最終更新日:2026/06/25

import bcrypt
import re

import FL0S001D
import FL0S099D

def login_check(user, password):
    user_info = FL0S001D.select_user(user)
    if not user_info:
        return 1, 0
    stored = user_info[3]
    if bcrypt.checkpw(password.encode('utf-8'), stored.encode('utf-8')):
        return 0, user_info[2]
    else:
        return 2, 0

def update_password(user_id,password):
    err = FL0S001D.update_password(user_id,password)
    err = FL0S099D.update_userPassword(user_id,password)
    return ""        
    
def get_user01():
    user_data = FL0S001D.select_all_users()
    return user_data

def get_user02(user_id):
    user_data = FL0S001D.select_user(user_id)
    status_dict = {
        0: "一般学生",
        1: "役付学生",
        2: "教官",
        3: "指導員",
        4: "指定養成教官",
        5: "監督",
        9: "管理者"
        }
    user_data[2] = status_dict[user_data[2]]
    user_data.pop()
    return user_data

def check02(name,status):
    if not name or not status:
        return "未入力項目があります。"
    if len(name) > 10:
        return "氏名は10字以内で入力してください。"
    try:
        dummy = int(status)
        if len(status) != 1:
            return "権限は1桁の数字で入力してください。"
    except ValueError:
        return "権限は半角数字で入力してください。"
    return ""

def check03(pass1,pass2):
    if pass1 != pass2:
        return "１回目と２回目で入力値が異なります。"
    else:
        if len(pass1) < 6 or len(pass1) > 30:
            return "パスワードは６字以上３０字以内で設定してください。"
        if not pass1.isalnum():
            return "パスワードは半角英数字で設定してください。"
        if not any(ix1.isdigit() for ix1 in pass1):
            return "パスワードは文字と数字を組み合わせてください。"
        if not any(ix1.isalpha() for ix1 in pass1):
            return "パスワードは文字と数字を組み合わせてください。"
        return ""

def check04(id, name):
    if len(id) != 7:
        return "ユーザーIDが不正な値です。"
    pattern = r'^\d{2}[A-Z]\d{4}$'
    if not re.match(pattern, id):
        return "ユーザーIDが不正な値です。"
    if len(name) > 10:
        return "氏名は10字以内で入力してください。"
    if ' ' in name or '　' in name:
        return "氏名は空白を入れずに入力してください。"
    return ""

def update_user(update_user):
    err = FL0S001D.update_user(update_user)
    return ""

def insert_user(id, name, status_cd):
    gakkaData = FL0S099D.select_userGakka(id)
    print(gakkaData)
    if gakkaData:
        password = gakkaData[5]
    else:
        password = FL0S001D.hash_password('245422kz')
    err = FL0S001D.insert_user(id, name, status_cd, password)
    if err == 3:
        return "入力したユーザーは登録済みです。"
    return ""    
