import psutil
import requests
import time
import socket
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logging.error("Конфигурационный файл config.json не найден!")
    exit(1)

INTERVAL = config.get('interval', 10)  # Интервал по умолчанию — 10 секунд
DASHBOARD_URL = config.get('dashboard_url', 'http://localhost:5000/api/metrics')

def collect_metrics():
    cpu = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters()
    net_sent = net.bytes_sent
    net_recv = net.bytes_recv
    return {
        'cpu': cpu,
        'memory': memory,
        'disk': disk,
        'net_sent': net_sent,
        'net_recv': net_recv
    }

def send_data(metrics):
    server_id = socket.gethostname()  # Имя хоста как идентификатор сервера
    data = {
        'server_id': server_id,
        'timestamp': time.time(),  # Временная метка
        'metrics': metrics
    }
    try:
        response = requests.post(DASHBOARD_URL, json=data, timeout=5)
        if response.status_code == 200:
            logging.info('Данные успешно отправлены')
        else:
            logging.warning(f'Ошибка отправки данных: код {response.status_code}')
    except requests.exceptions.RequestException as e:
        logging.error(f'Ошибка сети при отправке данных: {e}')

if __name__ == '__main__':
    logging.info('Агент мониторинга запущен')
    while True:
        metrics = collect_metrics()
        send_data(metrics)
        time.sleep(INTERVAL)