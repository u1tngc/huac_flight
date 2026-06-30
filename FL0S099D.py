#PGM-ID:FL0S099D
#PGM-NAME:FL学科関連ＤＢI/O(オンライン)
#最終更新日:2026/06/25

import psycopg2
import os
import bcrypt

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

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def get_gakuseiName(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 氏名 FROM "学生管理セグ" WHERE 学籍番号 = %s'
            data = (id,)
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

def get_gakuseiInfo01():
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT 学籍番号, 氏名 FROM "学生管理セグ" WHERE 権限 IN (0, 1, 6, 7)'
            cur.execute(sql)
            result = cur.fetchall()  
        conn.close()
        return [list(row) for row in result]
    except psycopg2.Error as e:
        print(f'エラー内容：{e}')
        return ""
    except Exception as e:
        print(f'エラー内容：{e}')
        return ""
    
def select_userGakka(id):
    try:
        conn = psycopg2.connect(**DB_CONFIG)  
        with conn.cursor() as cur:
            sql = 'SELECT * FROM "学生管理セグ" WHERE 学籍番号 = %s'
            data = (id,)
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
    
def update_userPassword(id, password):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            sql = "UPDATE 学生管理セグ SET パスワード = %s WHERE 学籍番号 = %s"
            data = (hash_password(password), id)
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
