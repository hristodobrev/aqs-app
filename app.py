from flask import Flask, request, render_template, jsonify
import sqlite3
import json
import datetime

app = Flask(__name__)


# TODO: date column should be renamed to created!


@app.template_filter()
def format_datetime(value, format='%Y-%m-%d'):
    value = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    return value.strftime(format)

@app.route("/average", methods=['GET'])
def average():
    db = sqlite3.connect('aqs-data.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute(
        "SELECT strftime('%H', date) as time, AVG(temperature) as avg_temp"
        " FROM data GROUP BY time ORDER BY date DESC LIMIT 24"
    )
    rows = cur.fetchall()

    return render_template('average.html', data=json.dumps([dict(row) for row in rows]))

@app.route("/current", methods=['GET'])
def getCurrentData():
    db = sqlite3.connect('aqs-data.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute(
        "SELECT p1, p2, temperature, pressure, humidity, (100 + signal) * 2 as signal, datetime(date, 'localtime') as date"
        " FROM data ORDER BY date desc LIMIT 1"
    )
    row = cur.fetchone()

    result = {
        "p1": row["p1"],
        "p2": row["p2"],
        "temperature": row["temperature"],
        "pressure": round(row["pressure"] / 100, 2),
        "humidity": row["humidity"],
        "signal": row["signal"],
        "date": datetime.datetime.strptime(row["date"], '%Y-%m-%d %H:%M:%S').strftime("%d/%m/%Y %H:%M:%S")
    }

    return jsonify(result)

@app.route("/data/<limit>", methods=['GET'])
@app.route("/data", methods=['GET'])
def getData(limit=50):
    db = sqlite3.connect('aqs-data.db')
    db.row_factory = sqlite3.Row
    cur = db.cursor()
    cur.execute(
        "SELECT p1, p2, temperature, pressure, humidity, (100 + signal) * 2 as signal,"
        " datetime(date, 'localtime') as date FROM data ORDER BY date desc LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()

    return render_template(
        'data.html',
        rowsJson=json.dumps([dict(row) for row in rows[::-1]]),
        rows=rows,
        date=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        nan=float('nan')
    )

@app.route("/data", methods=['POST'])
def saveData():
    
    data = request.get_json(force=True)
    valuesData = data['sensordatavalues']
    dictValues = {}
    for value in valuesData:
        dictValues[value["value_type"]] = value["value"]

    db = sqlite3.connect('aqs-data.db')
    cur = db.cursor()
    cur.execute(
        "INSERT INTO data (p1, p2, temperature, pressure, humidity, signal)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (
            dictValues['SDS_P1'], dictValues['SDS_P2'], dictValues['BME280_temperature'], 
            dictValues['BME280_pressure'], dictValues['BME280_humidity'], dictValues['signal']
        )
    )
    db.commit()
    db.close()

    return "Success"

@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html')

app.add_url_rule('/', endpoint='home')

app.run(debug=True, host='0.0.0.0', port='5001')