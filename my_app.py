from flask import Flask, jsonify, request
import requests
import pyodbc 
import pandas as pd
import json
import collections

app = Flask(__name__)

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=localhost\MSSQLSERVER01;'
                      'Database=index;'
                      'Trusted_Connection=yes;')

@app.route('/')
def api_information():
    return """<html>
<body>
<h1>APIs</h1>
<b>Get all the indexes</b>
<p>Request type: GET</p>
<p>Path: /indexes/</p>
<br></br>
<b>Get stock price data</b>
<p>Request type: GET</p>
<p>Path: /get_company_stock_data/"symbol"/"function"</p>
<p>Example Path: /get_company_stock_data/MCX/TIME_SERIES_MONTHLY</p>
<br></br>
<b>Add new index</b>
<p>Request type: POST</p>
<p>Path: /add_index</p>
<p>Example Body: {"pk_index_id": 10,
    "index_name": "TEST INDEX",
    "index_symbol": "TEST"}</p>
<br></br>
<b>Update index</b>
<p>Request type: PUT</p>
<p>Path: /update_index/"index_symbol"</p>
<p>Example Body: {
    "pk_index_id": "10",
    "index_name": "TEST INDEX 2"
}</p>
<br></br>
<b>Delete index</b>
<p>Request type: PUT</p>
<p>Path: /delete_index/"index_symbol"</p>
<br></br>
</body>
</html>"""

# Get Request
@app.route('/indexes/', methods=['GET'])
def get_indexes():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dbo.index_data')
        rows = cursor.fetchall()
        rowarray_list = []
        for row in rows:
            t = (row[0], row[1], row[2])
            rowarray_list.append(t)
        j = json.dumps(rowarray_list)
        # Convert query to objects of key-value pairs
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d["index_id"] = row[0]
            d["index_name"] = row[1]
            d["index_symbol"] = row[2]
            objects_list.append(d)
        j = json.dumps(objects_list)
        response = j
        return(response),200
    except:
        return jsonify({'error':'there was an error getting the indexes'}), 400

# External API Request
@app.route('/get_company_stock_data/<symbol>/<function>', methods=['GET'])
def get_companies_time_series(symbol, function):
    try:
        # Define the non-variable parameters
        ploads = {'datatype': 'json', 'apikey': '5VKW15ETPEN1FRNO'}
        # Update the variable parameters
        ploads['function'] = function
        ploads['symbol'] = symbol
        url = 'https://www.alphavantage.co/query?'
        # Make the get equest
        response = requests.get(url, params=ploads)
        # Extract the JSON response and convert it into a dictionary
        #response_dict = literal_eval(response.text)
        return jsonify(response.text),200
    except:
        return jsonify({'error':'there was an error getting the {symbol} stock data'}), 400

# Post Request
@app.route('/add_index', methods=['POST'])
def create_an_index():
    try:
        if not request.json or not 'pk_index_id' in request.json:
            return jsonify({'error':'the new index needs to have a pk_index_id'}), 400
        if not request.json or not 'index_name' in request.json:
            return jsonify({'error':'the new index needs to have a index_name'}), 400
        if not request.json or not 'index_symbol' in request.json:
            return jsonify({'error':'the new index needs to have a index_symbol'}), 400
        cursor = conn.cursor()
        pk_index_id = request.json['pk_index_id']
        index_name = request.json['index_name']
        index_symbol = request.json['index_symbol']
        script = f"INSERT INTO [dbo].[index_data] ([pk_index_id], [index_name], [index_symbol]) VALUES ({pk_index_id}, '{index_name}', '{index_symbol}')"
        #return jsonify(script)
        cursor.execute(script)
        return jsonify({'message':'new index created: {}'.format([index_name])}), 201
    except:
        return jsonify({f'error':'there was an error adding the index'}), 400


# Delete Request
@app.route('/delete_index/<index_symbol>', methods=['DELETE'])
def delete_index(index_symbol):
    try:
        cursor = conn.cursor()
        script = f"DELETE FROM [dbo].[index_data] WHERE [index_symbol] = '{index_symbol}'"
        cursor.execute(script)
        return jsonify({'success': True}), 200
    except:
        return jsonify({'success': False}), 400

# Push Request
@app.route('/update_index/<index_symbol>', methods=['PUT'])
def update_index(index_symbol):
    try:
        cursor = conn.cursor()
        if not request.json or not 'pk_index_id' in request.json:
            return jsonify({'error':'the updated index needs to have a pk_index_id'}), 400
        if not request.json or not 'index_name' in request.json:
            return jsonify({'error':'the updated index needs to have a index_name'}), 400
        pk_index_id = request.json['pk_index_id']
        index_name = request.json['index_name']
        script = f"UPDATE [dbo].[index_data] SET pk_index_id = '{pk_index_id}', index_name = '{index_name}' WHERE [index_symbol] = '{index_symbol}'"
        cursor.execute(script)
        return jsonify({'success': True}), 200
    except:
        return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

