import sqlite3

def create_connection():
    conn = sqlite3.connect('monitoring.db')
    return conn

def create_tables():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT,
            timestamp REAL,
            cpu REAL,
            memory REAL,
            disk REAL,
            net_sent INTEGER,
            net_recv INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            server_id TEXT,
            timestamp REAL,
            metric_type TEXT,
            threshold_value REAL,
            actual_value REAL
        )
    ''')
    conn.commit()
    conn.close()

def insert_metric(server_id, timestamp, cpu, memory, disk, net_sent, net_recv):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO metrics (server_id, timestamp, cpu, memory, disk, net_sent, net_recv)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (server_id, timestamp, cpu, memory, disk, net_sent, net_recv))
    conn.commit()
    conn.close()

def insert_alert(server_id, timestamp, metric_type, threshold_value, actual_value):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alerts (server_id, timestamp, metric_type, threshold_value, actual_value)
        VALUES (?, ?, ?, ?, ?)
    ''', (server_id, timestamp, metric_type, threshold_value, actual_value))
    conn.commit()
    conn.close()

def get_metrics(server_id=None):
    conn = create_connection()
    cursor = conn.cursor()
    if server_id:
        cursor.execute('SELECT * FROM metrics WHERE server_id = ? ORDER BY timestamp DESC LIMIT 100', (server_id,))
    else:
        cursor.execute('SELECT * FROM metrics ORDER BY timestamp DESC LIMIT 100')
    metrics = cursor.fetchall()
    conn.close()
    return metrics

def get_alerts():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 100')
    alerts = cursor.fetchall()
    conn.close()
    return alerts