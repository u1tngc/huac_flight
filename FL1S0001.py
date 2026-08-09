#PGM-ID:FL1S0001
#PGM-NAME:FLフライト管理履歴サブ
#最終更新日:2026/08/09

from datetime import datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta

import FL0S001D
import FL0S002D
import FL0S01XD
import FL0S099D

def get_rireki(id,kbn):
    if kbn == 1:
        list = FL0S002D.get_rireki(id,"F","1")
    elif kbn == 2:
        list = FL0S002D.get_rireki(id,"F","2")
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
    temp_array = FL0S01XD.get_kamokuList("F", str(kbn))
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

#履歴登録1（学生用）
def regist_rireki1(id, ymd, bangou, edaban, kyokan, comment):
    err = check_rireki(ymd, bangou, edaban, comment)
    if err:
        return err
    insert_data = [id, ymd, bangou[0:1], bangou[1:2], bangou[2:6], int(edaban), kyokan, comment]
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

def get_kinkyu_rireki():
    JST = timezone(timedelta(hours=9))
    kijunYmd =  (datetime.now(JST) - relativedelta(months=6)).strftime("%Y%m%d")
    gakusei_list = FL0S099D.get_gakuseiInfo01()
    ret_array = []
    for ix1 in range(len(gakusei_list)):
        temp_array = ["",0,"",0,"",0,"",0,""]
        subG = FL0S002D.get_rirekiSolo(gakusei_list[ix1][0], "F", "1")
        saku = FL0S002D.get_rirekiSolo(gakusei_list[ix1][0], "F", "2")
        spin = FL0S002D.get_rirekiSolo(gakusei_list[ix1][0], "F", "4")
        sissoku = FL0S002D.get_rirekiSolo(gakusei_list[ix1][0], "", "")
        temp_array[0] = gakusei_list[ix1][1]
        if not subG:
            temp_array[1] = 1
            temp_array[2] = "実施無"
        elif subG[1] < kijunYmd:
            temp_array[1] = 1
            temp_array[2] = datetime.strptime(subG[1], "%Y%m%d").strftime("%y/%m/%d")
        else:
            temp_array[1] = 0
            temp_array[2] = datetime.strptime(subG[1], "%Y%m%d").strftime("%y/%m/%d")
        if not saku:
            temp_array[3] = 1
            temp_array[4] = "実施無"
        elif saku[1] < kijunYmd:
            temp_array[3] = 1
            temp_array[4] = datetime.strptime(saku[1], "%Y%m%d").strftime("%y/%m/%d")
        else:
            temp_array[3] = 0
            temp_array[4] = datetime.strptime(saku[1], "%Y%m%d").strftime("%y/%m/%d")
        if not spin:
            temp_array[5] = 1
            temp_array[6] = "実施無"
        elif spin[1] < kijunYmd:
            temp_array[5] = 1
            temp_array[6] = datetime.strptime(spin[1], "%Y%m%d").strftime("%y/%m/%d")
        else:
            temp_array[5] = 0
            temp_array[6] = datetime.strptime(spin[1], "%Y%m%d").strftime("%y/%m/%d")
        if not sissoku:
            temp_array[7] = 1
            temp_array[8] = "実施無"
        elif sissoku[1] < kijunYmd:
            temp_array[7] = 1
            temp_array[8] = datetime.strptime(sissoku[1], "%Y%m%d").strftime("%y/%m/%d")
        else:
            temp_array[7] = 0
            temp_array[8] = datetime.strptime(sissoku[1], "%Y%m%d").strftime("%y/%m/%d")
        ret_array.append(temp_array)
    return ret_array
                
def get_SoloChk(id):
    ret_array0 = check_kinkyu(id)
    ret_array1 = check_Solo(id, ret_array0)
    if ret_array1[5] == 1:
        solo_kahi = 1
    ret_array2 = check_23iko(id, ret_array0, solo_kahi)
    ret_array3 = check_dis(id, ret_array0, solo_kahi)
    name = FL0S099D.get_gakuseiName(id)
    return name, ret_array0, ret_array1, ret_array2, ret_array3

def check_kinkyu(id):
    """
    0:サブＧ
    1:索切れ
    2:失速
    3:スピン
    """
    JST = timezone(timedelta(hours=9))
    kijunYmd =  (datetime.now(JST) - relativedelta(months=6)).strftime("%Y%m%d")
    ret_array = []
    jiyu_array = []
    kamoku_list = ["サブＧ", "索切れ", "失速", "スピン"]
    for ix1 in range(len(kamoku_list)):
        temp_array = [1,"未実施",""]
        if ix1 == 0:
            rireki = FL0S002D.get_rirekiSolo(id, "F", "1")
        elif ix1 == 1:
            rireki = FL0S002D.get_rirekiSolo(id, "F", "2")
        elif ix1 == 2:
            rireki = FL0S002D.get_rirekiSolo(id, "", "")
        elif ix1 == 3:
            rireki = FL0S002D.get_rirekiSolo(id, "F", "4")
        if not rireki:
            pass
        elif rireki[1] < kijunYmd:
            temp_array[2] = datetime.strptime(rireki[1], "%Y%m%d").strftime("%y/%m/%d")
        else:
            temp_array[0] = 0
            temp_array[1] = datetime.strptime(rireki[1], "%Y%m%d").strftime("%y/%m/%d")
            temp_array[2] = rireki[6]
        ret_array.append(temp_array)

    return ret_array

def check_Solo(id,kinkyu_array):
    """
    0:ノーダイブ
    1:横風着陸
    2:オーバーヘッド
    3:失速
    4:口述
    5:ソロ判定
    6:NG事由
    """
    ret_array = []
    jiyu_array = []
    kamoku_list = ["C1001", "C2001", "C3001", "1", "C5001"]
    kamoku_name = ["ノーダイブ", "横風着陸", "オーバーヘッド", "失速", "口述"]
    solo_NG_hantei = 0
    for ix1 in range(len(kamoku_list)):
        temp_array = [1, "未実施", ""]
        if kamoku_list[ix1] == "1":
            rireki = FL0S002D.get_rirekiSolo(id, "", "")
        else:
            rireki = FL0S002D.get_rirekiSolo(id, kamoku_list[ix1][0:1], kamoku_list[ix1][1:2])
        if rireki:
            temp_array[0] = 0
            temp_array[1] = datetime.strptime(rireki[1], "%Y%m%d").strftime("%Y/%m/%d")
            temp_array[2] = rireki[6]
        else:
            solo_NG_hantei = 1
            jiyu = f"【{kamoku_name[ix1]}】が未実施"
            jiyu_array.append(jiyu)
        ret_array.append(temp_array)
    if kinkyu_array[0][0] == 1:
        solo_NG_hantei = 1
        jiyu_array.append("サブＧが未実施もしくは６ヵ月以内に実施無し")
    if kinkyu_array[2][0] == 1:
        solo_NG_hantei = 1
        jiyu_array.append("失速が未実施もしくは６ヵ月以内に実施無し")
    if kinkyu_array[3][0] == 1:
        solo_NG_hantei = 1
        jiyu_array.append("スピン（初動含む）が未実施もしくは６ヵ月以内に実施無し")
    if solo_NG_hantei == 1:
        ret_array.append(1)
        ret_array.append(jiyu_array)
    else:
        ret_array.append(0)
        ret_array.append("")
    return ret_array

def check_23iko(id, kinkyu_array, solo_kahi):
    """
    0:Ａ章
    1:Ｂ章
    2:２３移行口述
    3:学科
    4:判定
    5:NG事由
    """
    ret_array = []
    jiyu_array = []
    kamoku_list = ["C6001", "D1001", "D2001"]
    kamoku_name = ["Ａ章", "Ｂ章", "２３移行口述"]
    solo_NG_hantei = 0
    if solo_kahi == 1:
            solo_NG_hantei = 1
            jiyu_array.append(f"ソロ要件を満たしていない")
    for ix1 in range(len(kamoku_list)):
        temp_array = [1, "未実施", "-"]
        if kamoku_list[ix1] == "1":
            rireki = FL0S002D.get_rirekiSolo(id, "", "")
        else:
            rireki = FL0S002D.get_rirekiSolo(id, kamoku_list[ix1][0:1], kamoku_list[ix1][1:2])
        if rireki:
            temp_array[0] = 0
            temp_array[1] = datetime.strptime(rireki[1], "%Y%m%d").strftime("%Y/%m/%d")
            temp_array[2] = rireki[6]
        else:
            solo_NG_hantei = 1
            jiyu = f"【{kamoku_name[ix1]}】が未実施"
            jiyu_array.append(jiyu)
        ret_array.append(temp_array)
    test_num = check_test(id)
    if test_num > 2:
        ret_array.append([0, "問題なし", "-"])
    else:
        solo_NG_hantei = 1
        ret_array.append([1, "NG", "-"])
        jiyu_array.append("中間CHKの合格数が２件未満")
    kinkyu = ["サブＧ","索切れ","失速","スピン（初動含む）"]
    for ix1 in range(len(kinkyu_array)):
        if kinkyu_array[ix1][0] == 1:
            solo_NG_hantei = 1
            jiyu_array.append(f"【{kinkyu[ix1]}】が未実施もしくは６ヵ月以内に実施無し")
    if solo_NG_hantei == 1:
        ret_array.append(1)
        ret_array.append(jiyu_array)
    else:
        ret_array.append(0)
        ret_array.append("")
    return ret_array

def check_dis(id, kinkyu_array, solo_kahi):
    """
    0:アーカス搭乗
    1:口述
    2:自家用
    3:判定
    4:NG事由
    """
    ret_array = []
    jiyu_array = []
    kamoku_list = ["G1001", "G2001"]
    kamoku_name = ["アーカス搭乗", "口述"]
    solo_NG_hantei = 0
    if solo_kahi == 1:
            solo_NG_hantei = 1
            jiyu_array.append(f"ソロ要件を満たしていない")
    for ix1 in range(len(kamoku_list)):
        temp_array = [1, "未実施", "-"]
        if kamoku_list[ix1] == "1":
            rireki = FL0S002D.get_rirekiSolo(id, "", "")
        else:
            rireki = FL0S002D.get_rirekiSolo(id, kamoku_list[ix1][0:1], kamoku_list[ix1][1:2])
        if rireki:
            temp_array[0] = 0
            temp_array[1] = datetime.strptime(rireki[1], "%Y%m%d").strftime("%Y/%m/%d")
            temp_array[2] = rireki[6]
        else:
            solo_NG_hantei = 1
            jiyu = f"【{kamoku_name[ix1]}】が未実施"
            jiyu_array.append(jiyu)
        ret_array.append(temp_array)
    shikaku = FL0S099D.get_shikaku(id)
    if shikaku == 0:
        solo_NG_hantei = 1
        ret_array.append([1, "練許生", "-"])
        jiyu_array.append("自家用資格がありません。")
    else:
        ret_array.append([0, "自家用資格あり", "-"])
    kinkyu = ["サブＧ","索切れ","失速","スピン（初動含む）"]
    for ix1 in range(len(kinkyu_array)):
        if kinkyu_array[ix1][0] == 1:
            solo_NG_hantei = 1
            jiyu_array.append(f"【{kinkyu[ix1]}】が未実施もしくは６ヵ月以内に実施無し")
    if solo_NG_hantei == 1:
        ret_array.append(1)
        ret_array.append(jiyu_array)
    else:
        ret_array.append(0)
        ret_array.append("")
    return ret_array

def get_kyokanList():
    ret_array = FL0S001D.get_kyokanList()
    return [row[0] for row in ret_array]

def check_test(id):
    shikaku = FL0S099D.get_shikaku(id)
    if shikaku == 0:
        temp_array = FL0S099D.get_test(id)
        num = 0
        if temp_array[2]:
            num = num + 1
        if temp_array[3]:  
            num = num + 1
        if temp_array[4]:
            num = num + 1
        if temp_array[5]:
            num = num + 1
        return num
    else:
        return 4