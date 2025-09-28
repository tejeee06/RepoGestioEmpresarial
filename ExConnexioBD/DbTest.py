import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "erp_demo",
    "port": "3306",
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT ClientId, nom, email, telefon, ciutat FROM client ORDER BY ClientId;")

    for fila in cur.fetchall():
        print(fila)
        
    cur.close()
    conn.close()

except Error as e:
    print("[ERROR MySQL]", e)
