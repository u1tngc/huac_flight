#PGM-ID:FL0S002D
#PGM-NAME:FL課目履歴セグI/O(オンライン)
#最終更新日:2026/08/14

import psycopg2
import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": 26257,
    "sslmode": "require",
    "sslcert": "",
    "sslkey": "",
    "sslrootcert": "",
    "target_session_attrs": "read-write"
}

#表示順：実施年月日（降順）＞分野（昇順）＞区分（昇順）＞番号（昇順）＞枝番（降順）
ORDER_RIREKI = ' ORDER BY 実施年月日 DESC, 分野 ASC, 区分 ASC, 番号 ASC, 枝番 DESC'
ORDER_RIREKI_R = ' ORDER BY r.実施年月日 DESC, r.分野 ASC, r.区分 ASC, r.番号 ASC, r.枝番 DESC'

def get_rireki(id,bunya,kbn):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            if bunya == "F":
                if isinstance(kbn, (list, tuple)):
                    sql = 'SELECT * FROM "課目履歴セグ" WHERE 学籍番号 = %s AND 分野 = %s AND 区分 = ANY(%s)' + ORDER_RIREKI
                    data = (id,bunya,list(kbn))
                else:
                    sql = 'SELECT * FROM "課目履歴セグ" WHERE 学籍番号 = %s AND 分野 = %s AND 区分 = %s' + ORDER_RIREKI
                    data = (id,bunya,kbn)
            elif kbn == "3":
                #学生（権限0,1）用：登録可能な課目（更新区分＝０）の履歴に限定する
                sql = ('SELECT r.* FROM "課目履歴セグ" AS r '
                       'JOIN "課目cdセグ" AS c ON r.分野 = c.分野 AND r.区分 = c.区分 AND r.番号 = c.番号 '
                       'WHERE r.学籍番号 = %s AND c.更新区分 = 0') + ORDER_RIREKI_R
                data = (id,)
            else:
                sql = 'SELECT * FROM "課目履歴セグ" WHERE 学籍番号 = %s AND 分野 != %s' + ORDER_RIREKI
                data = (id,"F")
            cur.execute(sql,data)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []

def insert_rireki(insert_data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'INSERT INTO "課目履歴セグ" (学籍番号, 実施年月日, 分野, 区分, 番号, 枝番, 教官, コメント) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            data = (insert_data[0], insert_data[1], insert_data[2], insert_data[3], insert_data[4], insert_data[5], insert_data[6], insert_data[7])
            cur.execute(sql, data)
            conn.commit()
        return 0
    except psycopg2.IntegrityError as e:
        print(f'エラー内容：{e}')
        return 3
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2
    finally:
        if conn:
            conn.close()

def update_rireki(comment, key_data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'UPDATE "課目履歴セグ" SET コメント = %s WHERE 学籍番号 = %s AND 実施年月日 = %s AND 分野 = %s AND 区分 = %s AND 番号 = %s AND 枝番 = %s'
            data = (comment, key_data[0], key_data[1], key_data[2], key_data[3], key_data[4], key_data[5])
            cur.execute(sql, data)
            conn.commit()
        conn.close()
        return 0
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2

def delete_rireki(key_data):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'DELETE FROM "課目履歴セグ" WHERE 学籍番号 = %s AND 実施年月日 = %s AND 分野 = %s AND 区分 = %s AND 番号 = %s AND 枝番 = %s'
            data = (key_data[0], key_data[1], key_data[2], key_data[3], key_data[4], key_data[5])
            cur.execute(sql, data)
            #該当データが無い場合は削除件数0として通知する
            if cur.rowcount == 0:
                conn.rollback()
                conn.close()
                return 3
            conn.commit()
        conn.close()
        return 0
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        return 2

#以降、excel出力用
_cacheSolo = None

def load_cacheSolo():
    global _cacheSolo
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = (
                'SELECT 学籍番号, 実施年月日, 分野, 区分, 番号, 枝番, 教官, コメント '
                'FROM "課目履歴セグ" '
                'ORDER BY 実施年月日 DESC, 番号 ASC, 枝番 ASC'
            )
            cur.execute(sql)
            result = cur.fetchall()
        conn.close()
        cache = {}
        for row in result:
            key = (row[0], row[2], row[3])
            if key not in cache:
                cache[key] = list(row)
        _cacheSolo = cache
        return 0
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        _cacheSolo = None
        return 1
    except Exception as e:
        print(f'エラー内容：{e}')
        _cacheSolo = None
        return 1

def clear_cacheSolo():
    global _cacheSolo
    _cacheSolo = None

def _get_rirekiSoloCache(id, bunya, kbn):
    if bunya == "":
        cand = [_cacheSolo.get((id, "E", "2")), _cacheSolo.get((id, "C", "4"))]
        cand = [row for row in cand if row]
    else:
        row = _cacheSolo.get((id, bunya, kbn))
        cand = [row] if row else []
    if not cand:
        return []
    cand.sort(key=lambda row: (row[4], row[5]))
    cand.sort(key=lambda row: row[1], reverse=True)
    return list(cand[0])

def get_rirekiSolo(id, bunya, kbn):
    if _cacheSolo is not None:
        return _get_rirekiSoloCache(id, bunya, kbn)
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            if bunya == "":
                sql = (
                    'SELECT * FROM "課目履歴セグ" '
                    'WHERE 学籍番号 = %s AND ((分野 = %s AND 区分 = %s) OR (分野 = %s AND 区分 = %s)) '
                    'ORDER BY 実施年月日 DESC, 番号 ASC, 枝番 ASC '
                    'LIMIT 1'
                )
                data = (id, 'E', '2', 'C', '4')
            else:
                sql = (
                    'SELECT * FROM "課目履歴セグ" '
                    'WHERE 学籍番号 = %s AND 分野 = %s AND 区分 = %s '
                    'ORDER BY 実施年月日 DESC, 番号 ASC, 枝番 ASC '
                    'LIMIT 1'
                )
                data = (id, bunya, kbn)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return list(result) if result else []
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []