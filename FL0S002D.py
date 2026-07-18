#PGM-ID:FL0S002D
#PGM-NAME:FL緊急課目履歴セグI/O(オンライン)
#最終更新日:2026/06/26

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


def get_rireki(id,bunya,kbn):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            if bunya == "D":
                sql = 'SELECT * FROM "緊急課目履歴セグ" WHERE 学籍番号 = %s AND 分野 = %s AND 区分 = %s'
                data = (id,bunya,kbn)
            else:
                sql = 'SELECT * FROM "緊急課目履歴セグ" WHERE 学籍番号 = %s AND 分野 != %s'
                data = (id,"D")
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
            sql = 'INSERT INTO "緊急課目履歴セグ" (学籍番号, 実施年月日, 分野, 区分, 番号, 枝番, 教官, コメント) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
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
            sql = 'UPDATE "緊急課目履歴セグ" SET コメント = %s WHERE 学籍番号 = %s AND 実施年月日 = %s AND 分野 = %s AND 区分 = %s AND 番号 = %s AND 枝番 = %s'
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

def get_rirekiSolo(id, bunya, kbn):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = (
                'SELECT * FROM "緊急課目履歴セグ" '
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