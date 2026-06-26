#PGM-ID:FL1S0001
#PGM-NAME:FLフライト管理履歴サブ
#最終更新日:2026/06/25

import FL0S001D
import FL0S002D
import FL0S01XD
    
def get_rireki(id,kbn):
    if kbn == 1:
        list = FL0S002D.get_rireki(id,"D","1")
    elif kbn == 2:
        list = FL0S002D.get_rireki(id,"D","2") 
    ret_array = []
    if list:
        name = FL0S001D.get_gakuseiName(id)
        for ix1 in range(len(list)):
            temp_array = [""]*5
            temp_array[0] = name
            temp_array[1] = list[ix1][1]
            temp_array[2] = FL0S01XD.get_kamoku(list[ix1][2],list[ix1][3],list[ix1][4])
            temp_array[3] = list[ix1][6]
            temp_array[4] = list[ix1][7]
            ret_array.append(temp_array)
    print(ret_array)
    return ret_array

def get_gakuseiInfo01():
    ret_array = FL0S001D.get_gakuseiInfo01()
    return ret_array