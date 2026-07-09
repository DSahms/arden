from flask import Flask, request, jsonify, render_template_string
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), 'dashboard.db')

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT NOT NULL,
            date TEXT NOT NULL,
            concern_level TEXT NOT NULL,
            sentiment_score INTEGER DEFAULT 0,
            isolation_score INTEGER DEFAULT 0,
            late_night INTEGER DEFAULT 0,
            message_length INTEGER DEFAULT 0,
            received_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/sync', methods=['POST'])
def sync():
    expected = os.environ.get('NURA_SYNC_TOKEN', '').strip()
    if expected:
        token = request.headers.get('X-NURA-Sync-Token', '').strip()
        if token != expected:
            return jsonify({'status': 'unauthorized'}), 401

    data = request.json or {}
    device_code = data.get('device_code') or data.get('patient_id', 'unknown')
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        INSERT INTO observations
        (patient_id, date, concern_level, sentiment_score, 
         isolation_score, late_night, message_length, received_at)
        VALUES (?,?,?,?,?,?,?,?)
    ''', (
        device_code,
        data.get('date'),
        data.get('concern_level', 'green'),
        data.get('sentiment_score', 0),
        data.get('isolation_score', 0),
        data.get('late_night', 0),
        data.get('message_length', 0),
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/')
def dashboard():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''
        SELECT patient_id, date, concern_level, 
               sentiment_score, isolation_score, late_night
        FROM observations
        ORDER BY id DESC
    ''')
    rows = c.fetchall()
    conn.close()

    color_map = {
        'green': '#2ecc71',
        'yellow': '#f1c40f', 
        'orange': '#e67e22',
        'red': '#e74c3c'
    }

    rows_html = ''
    for row in rows:
        color = color_map.get(row[2], '#2ecc71')
        late = '🌙' if row[5] else ''
        rows_html += f'''
        <tr>
            <td>{row[0]}</td>
            <td><span style="background:{color};padding:4px 12px;
                border-radius:12px;color:white;font-weight:bold;">
                {row[2].upper()}</span></td>
            <td>{row[1]}</td>
            <td>
                {late if late else ''}
                {'⚠️ Negative language' if row[3] > 0 else ''}
                {'🚪 Isolating' if row[4] > 0 else ''}
                {'✅ All clear' if row[3] == 0 and row[4] == 0 and not late else ''}
            </td>
        </tr>'''

    html = f'''<!DOCTYPE html>
<html>
<head>
    <title>NURA — Facility Dashboard</title>
    <meta http-equiv="refresh" content="60">
    <style>
        body {{ font-family: Arial, sans-serif; 
                background: #1a1a2e; color: #eee; padding: 20px; }}
        h1 {{ color: #5da9ff; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #16213e; padding: 12px; text-align: left; 
              color: #5da9ff; }}
        td {{ padding: 12px; border-bottom: 1px solid #333; }}
        tr:hover {{ background: #16213e; }}
    </style>
</head>
<body>
    <h1>NURA — Facility Dashboard</h1>
    <p style="color:#888">Auto-refreshes every 60 seconds — 
       {datetime.now().strftime("%B %d, %Y %I:%M %p")}</p>
    <table>
        <tr>
            <th>Device code</th>
            <th>Status</th>
            <th>Date</th>
            <th>Signals</th>
        </tr>
        {rows_html}
    </table>
    <p style="color:#888;margin-top:24px;font-size:13px;max-width:720px;line-height:1.6;">
        <b style="color:#ccc;">Signals only.</b> Concern level, pattern flags, late-night use.
        No message text. No conversation content. Device codes — not resident names.
        Counselor matches code to person on their own schedule.
    </p>
</body>
</html>'''
    return html

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
