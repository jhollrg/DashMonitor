from flask import Flask, render_template, request, jsonify
import json
from database import create_tables, insert_metric, insert_alert, get_metrics, get_alerts

app = Flask(__name__)

with open('config.json', 'r') as f:
    config = json.load(f)

THRESHOLDS = config.get('thresholds', {
    'cpu': 80,
    'memory': 80,
    'disk': 80
})


@app.route('/')
def index():
    metrics = get_metrics()
    servers = list(set([m[1] for m in metrics]))  # Uniques server_id
    return render_template('index.html', servers=servers)


@app.route('/server/<server_id>')
def server_details(server_id):
    """Server datails page"""
    metrics = get_metrics(server_id)
    return render_template('server_details.html', metrics=metrics, server_id=server_id)


@app.route('/alerts')
def alerts():
    alerts = get_alerts()
    return render_template('alerts.html', alerts=alerts)


@app.route('/api/metrics', methods=['POST'])
def receive_metrics():
    """API for receive metrics from agents"""
    data = request.json
    server_id = data['server_id']
    timestamp = data['timestamp']
    metrics = data['metrics']
    insert_metric(server_id, timestamp, metrics['cpu'], metrics['memory'], metrics['disk'],
                  metrics['net_sent'], metrics['net_recv'])

    # Checking edge-values
    if metrics['cpu'] > THRESHOLDS['cpu']:
        insert_alert(server_id, timestamp, 'cpu', THRESHOLDS['cpu'], metrics['cpu'])
    if metrics['memory'] > THRESHOLDS['memory']:
        insert_alert(server_id, timestamp, 'memory', THRESHOLDS['memory'], metrics['memory'])
    if metrics['disk'] > THRESHOLDS['disk']:
        insert_alert(server_id, timestamp, 'disk', THRESHOLDS['disk'], metrics['disk'])

    return jsonify({'status': 'success'}), 200


if __name__ == '__main__':
    create_tables()
    app.run(debug=True)