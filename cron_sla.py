import mysql.connector
from mysql.connector import Error
from datetime import datetime

db_config = {
    # 'host': 'localhost',
    'host': 'root',
    # 'user': 'dbuserA308',
    'user': 'root',
    # 'password': 'Nsdl@12345%',
    'password': 'root',
    'database': 'OTRS_ticketing_db'
}

def update_sla_status():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            now = datetime.now()
            update_query = update_query = """
            UPDATE SLA_log
            SET sla_status = 'breached'
            WHERE sla_due < %s
              AND ticket_status = 'open'
              AND created_at >= NOW() - INTERVAL 7 DAY
              AND sla_status != 'breached';
            """

            cursor.execute(update_query, (now,))
            connection.commit()
            print(f"Updated rows: {cursor.rowcount}")

    except Error as e:
        print(f"Error: ",e)

update_sla_status()
