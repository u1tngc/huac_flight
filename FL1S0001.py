#PGM-ID:FL1S0001
#PGM-NAME:FLフライト管理履歴サブ
#最終更新日:2026/07/18

from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

import FL0S001D
import FL0S002D
import FL0S01XD
import FL0S099D

def get_rireki(id,kbn):
    if kbn == 1:
        list = FL0S002D.get_rireki(id,"D","1")
    elif kbn == 2:
        list = FL0S002D.get_rireki(id,"D","2")
    ret_array = []
    if list:
        name = FL0S099D.get_gakuseiName(id)
        for ix1 in range(len(list)):
            temp_array = [""]*5
            temp_array[0] = name
            temp_array[1] = datetime.strptime(list[ix1][1], "%Y%m%d").strftime("%Y/%m/%d")
            temp_array[2] = FL0S01XD.get_kamoku(list[ix1][2],list[ix1][3],list[ix1][4])
            temp_array[3] = list[ix1][6]
            temp_array[4] = list[ix1][7]
            ret_array.append(temp_array)
    return ret_array

def get_gakuseiInfo01():
    ret_array = FL0S099D.get_gakuseiInfo01()
    return ret_array

def get_gakuseiName(id):
    name = FL0S099D.get_gakuseiName(id)
    return name

#更新画面用：課目選択肢（区分別）を取得
def get_kamokuList(kbn):
    temp_array = FL0S01XD.get_kamokuList("D", str(kbn))
    ret_array = []
    for ix1 in range(len(temp_array)):
        kamoku_no = temp_array[ix1][0]+temp_array[ix1][1]+temp_array[ix1][2]
        ret_array.append([kamoku_no, temp_array[ix1][3]])
    return ret_array

#更新画面用：キー項目込みの履歴一覧を取得
def get_rirekiEdit(id, bunya, kbn):
    list = FL0S002D.get_rireki(id, bunya, str(kbn))
    ret_array = []
    if list:
        for ix1 in range(len(list)):
            temp_array = [""]*6
            temp_array[0] = list[ix1][1]
            temp_array[1] = list[ix1][2]+list[ix1][3]+list[ix1][4]
            temp_array[2] = list[ix1][5]
            temp_array[3] = FL0S01XD.get_kamoku(list[ix1][2],list[ix1][3],list[ix1][4])
            temp_array[4] = list[ix1][6]
            temp_array[5] = list[ix1][7]
            ret_array.append(temp_array)
    return ret_array

#入力チェック
def check_rireki(ymd, bangou, edaban, comment):
    if not ymd or not bangou or not edaban:
        return "未入力項目があります。"
    if len(ymd) != 8 or not ymd.isdigit():
        return "実施年月日はYYYYMMDD形式の8桁の数字で入力してください。"
    try:
        dummy = datetime.strptime(ymd, "%Y%m%d")
    except ValueError:
        return "実施年月日が正しくありません。"
    try:
        eda = int(edaban)
        if len(edaban) != 1 or eda < 1:
            return "枝番は1以上の1桁の数字で入力してください。"
    except ValueError:
        return "枝番は半角数字で入力してください。"
    # if len(bangou) != 3:
    #     return "課目が正しくありません。"
    if len(comment) > 255:
        return "コメントは255字以内で入力してください。"
    return ""

#履歴登録
def regist_rireki(id, ymd, bangou, edaban, comment, user_id):
    err = check_rireki(ymd, bangou, edaban, comment)
    if err:
        return err
    name = FL0S001D.get_userName(user_id)
    insert_data = [id, ymd, bangou[0:1], bangou[1:2], bangou[2:6], int(edaban), name, comment]
    ret = FL0S002D.insert_rireki(insert_data)
    if ret == 3:
        return "同一の履歴が既に登録されています。"
    if ret != 0:
        return "登録に失敗しました。"
    return ""

#履歴訂正（コメント）
def correct_rireki(id, ymd, bunya, kbn, bangou, edaban, comment):
    if len(comment) > 255:
        return "コメントは255字以内で入力してください。"
    key_data = [id, ymd, bunya, str(kbn), bangou, int(edaban)]
    ret = FL0S002D.update_rireki(comment, key_data)
    if ret != 0:
        return "訂正に失敗しました。"
    return ""

def get_solo_chk():
    JST = timezone(timedelta(hours=9))
    kijunYmd =  (datetime.now(JST) - relativedelta(months=3)).strftime("%Y%m%d")
    gakusei_list = FL0S099D.get_gakuseiInfo01()
    ret_array = []
    for ix1 in range(len(gakusei_list)):
        temp_array = ["",0,"",0,""]
        subG = FL0S002D.get_rirekiSolo(gakusei_list[ix1][0], "D", "1")
        saku = FL0S002D.get_rirekiSolo(gakusei_list[ix1][0], "D", "2")
        temp_array[0] = gakusei_list[ix1][1]
        if not subG:
            temp_array[1] = 1
            temp_array[2] = "実施無し"
        elif subG[1] < kijunYmd:
            temp_array[1] = 1
            temp_array[2] = datetime.strptime(subG[1], "%Y%m%d").strftime("%Y/%m/%d")
        else:
            temp_array[1] = 0
            temp_array[2] = datetime.strptime(subG[1], "%Y%m%d").strftime("%Y/%m/%d")
        if not saku:
            temp_array[3] = 1
            temp_array[4] = "実施無し"
        elif saku[1] < kijunYmd:
            temp_array[3] = 1
            temp_array[4] = datetime.strptime(saku[1], "%Y%m%d").strftime("%Y/%m/%d")
        else:
            temp_array[3] = 0
            temp_array[4] = datetime.strptime(saku[1], "%Y%m%d").strftime("%Y/%m/%d")
        ret_array.append(temp_array)
    return ret_array
                
def get_1stSoloChk(id):
    ret_array = []
    kamoku_list = ["C1001", "C2001", "C3001", "C4001", "C5001"]
    gakuseiName = FL0S099D.get_gakuseiName(id)
    solo_NG_hantei = 0
    for ix1 in range(len(kamoku_list)):
        temp_array = [gakuseiName, 0, "未実施", ""]
        rireki = FL0S002D.get_rirekiSolo(id, kamoku_list[ix1][0:1], kamoku_list[ix1][1:2])
        if rireki:
            temp_array[0] = gakuseiName
            temp_array[1] = 1
            temp_array[2] = datetime.strptime(rireki[1], "%Y%m%d").strftime("%Y/%m/%d")
            temp_array[3] = rireki[6]
        else:
            solo_NG_hantei = 1
        ret_array.append(temp_array)
    if solo_NG_hantei == 1:
        ret_array.append(["ＮＧ", 0, "", ""])
    else:
        ret_array.append(["ＯＫ", 0, "", ""])
    return ret_array