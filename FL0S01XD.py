#PGM-ID:FL0S01XD
#PGM-NAME:FL課目ＣＤ管理セグI/O(オンライン)
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


def get_kamoku(bunya,kbn,bangou):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT 課目名 FROM "課目cdセグ" WHERE 分野 = %s AND 区分 = %s AND 番号 = %s '
            data = (bunya,kbn,bangou)
            cur.execute(sql, data)
            result = cur.fetchone()
        conn.close()
        return result[0] if result else ""
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""

def get_kamokuList(bunya,kbn):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = 'SELECT 番号, 課目名 FROM "課目cdセグ" WHERE 分野 = %s AND 区分 = %s ORDER BY 番号'
            data = (bunya,kbn)
            cur.execute(sql, data)
            result = cur.fetchall()
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return []
    except Exception as e:
        print(f'エラー内容：{e}')
        return []