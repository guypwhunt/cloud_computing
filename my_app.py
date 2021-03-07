# Import the necessary libraries
from flask import Flask, jsonify, request, render_template
import requests
import requests_cache
import pyodbc 
import pandas as pd
import json
import collections

requests_cache.install_cache('index_api_cache', backend='sqlite', expire_after=36000)

app = Flask(__name__)

# Define the connection parameters for the SQL database
conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=localhost\MSSQLSERVER01;'
                      'Database=index;'
                      'Trusted_Connection=yes;')

@app.route('/')
def api_information():
    # This function returns a HTML page with information on all the other APIs
    return """<html>
<body>
<h1>APIs</h1>
<b>Get all the indexes</b>
<p>Request type: GET</p>
<p>Path: /indexes/</p>
<br></br>
<b>Get a specific index</b>
<p>Request type: GET</p>
<p>Path: /indexes/"symbol"</p>
<p>Example Path: /indexes/MCX</p>
<br></br>
<b>Get stock price data</b>
<p>Request type: GET</p>
<p>Path: /indexes/stock_data/"symbol"/"function"</p>
<p>Example Path: /indexes/stock_data/MCX/TIME_SERIES_MONTHLY</p>
<br></br>
<b>Add new index</b>
<p>Request type: POST</p>
<p>Path: /indexes/add_index</p>
<p>Example Body: {"pk_index_id": 10,
    "index_name": "TEST INDEX",
    "index_symbol": "TEST"}</p>
<br></br>
<b>Update index</b>
<p>Request type: PUT</p>
<p>Path: /indexes/update_index/"index_symbol"</p>
<p>Example Body: {
    "pk_index_id": "10",
    "index_name": "TEST INDEX 2"
}</p>
<br></br>
<b>Delete index</b>
<p>Request type: PUT</p>
<p>Path: /indexes/delete_index/"index_symbol"</p>
<br></br>
</body>
</html>"""

# Get Request
@app.route('/indexes/', methods=['GET'])
def get_indexes():
    # This function gets all the indexes in the database
    try:
        # Open a connection to the database
        cursor = conn.cursor()

        # Perform the select statement and extract the rows
        cursor.execute('SELECT * FROM dbo.index_data')
        rows = cursor.fetchall()

        # For each row append the relevant data to an array
        rowarray_list = []
        for row in rows:
            t = (row[0], row[1], row[2])
            rowarray_list.append(t)

        # Convert the array into JSON
        j = json.dumps(rowarray_list)

        # Convert JSON to key-value pairs
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d["index_id"] = row[0]
            d["index_name"] = row[1]
            d["index_symbol"] = row[2]
            objects_list.append(d)
        
        # Convert key-value pairs to JSON
        response = json.dumps(objects_list)
        return(response),200
    except:
        return jsonify({'error':'there was an error getting the indexes'}), 400

# Get Request
@app.route('/indexes/<symbol>', methods=['GET'])
def get_index(symbol):
    # This function gets a specific index from the database
    try:
        # Open a connection to the database
        cursor = conn.cursor()

        # Perform the select statement and extract the rows for the index
        sql_script = f"SELECT * FROM dbo.index_data WHERE index_symbol = '{symbol}'"
        cursor.execute(sql_script)
        rows = cursor.fetchall()

        # For each row append the relevant data to an array
        rowarray_list = []
        for row in rows:
            t = (row[0], row[1], row[2])
            rowarray_list.append(t)

        # Convert the array into JSON
        j = json.dumps(rowarray_list)

        # Convert JSON to key-value pairs
        objects_list = []
        for row in rows:
            d = collections.OrderedDict()
            d["index_id"] = row[0]
            d["index_name"] = row[1]
            d["index_symbol"] = row[2]
            objects_list.append(d)

        # Convert key-value pairs to JSON
        response = json.dumps(objects_list)
        return(response),200
    except:
        return jsonify({'error':'there was an error getting the indexes'}), 400
    
# External API Request
@app.route('/indexes/stock_data/<symbol>/<function>', methods=['GET'])
def get_companies_time_series(symbol, function):
    # This function gets the indexes stock price time series data
    try:
        # Define the non-variable API parameters 
        ploads = {'datatype': 'json', 'apikey': '5VKW15ETPEN1FRNO'}
        url = 'https://www.alphavantage.co/query?'

        # Update the variable parameters
        ploads['function'] = function
        ploads['symbol'] = symbol
        
        # Make the get equest
        response = requests.get(url, params=ploads)

        return(json.loads(response.text)),200
    except:
        return jsonify({f'error':'there was an error getting the {symbol} stock data'}), 400

# Post Request
@app.route('/indexes/add_index', methods=['POST'])
def create_an_index():
    # This function allows users to add an index to the database
    try:
        # Identify if the body contains all the necessary data
        if not request.json or not 'pk_index_id' in request.json:
            return jsonify({'error':'the new index needs to have a pk_index_id'}), 400
        if not request.json or not 'index_name' in request.json:
            return jsonify({'error':'the new index needs to have a index_name'}), 400
        if not request.json or not 'index_symbol' in request.json:
            return jsonify({'error':'the new index needs to have a index_symbol'}), 400

        # Open a connection to the database
        cursor = conn.cursor()

        # Define input variables
        pk_index_id = request.json['pk_index_id']
        index_name = request.json['index_name']
        index_symbol = request.json['index_symbol']

        # Create the appropriate SQL script
        script = f"INSERT INTO [dbo].[index_data] ([pk_index_id], [index_name], [index_symbol]) VALUES ({pk_index_id}, '{index_name}', '{index_symbol}')"

        # Execute the SQL statement
        cursor.execute(script)
        return jsonify({'message':'new index created: {}'.format([index_name])}), 201
    except:
        return jsonify({f'error':'there was an error adding the index'}), 400


# Delete Request
@app.route('/indexes/delete_index/<index_symbol>', methods=['DELETE'])
def delete_index(index_symbol):
    # This function allows user to delete an index
    try:
        # Open a connection to the database
        cursor = conn.cursor()

        # Create the appropriate SQL script
        script = f"DELETE FROM [dbo].[index_data] WHERE [index_symbol] = '{index_symbol}'"

        # Execute the SQL statement
        cursor.execute(script)
        return jsonify({'success': True}), 200
    except:
        return jsonify({'success': False}), 400

# Push Request
@app.route('/indexes/update_index/<index_symbol>', methods=['PUT'])
def update_index(index_symbol):
    # This function allows users to update an index
    try:
        # Open a connection to the database
        cursor = conn.cursor()

        # Identify if the body contains all the necessary data
        if not request.json or not 'pk_index_id' in request.json:
            return jsonify({'error':'the updated index needs to have a pk_index_id'}), 400
        if not request.json or not 'index_name' in request.json:
            return jsonify({'error':'the updated index needs to have a index_name'}), 400
        
        # Define input variables
        pk_index_id = request.json['pk_index_id']
        index_name = request.json['index_name']

        # Create the appropriate SQL script
        script = f"UPDATE [dbo].[index_data] SET pk_index_id = '{pk_index_id}', index_name = '{index_name}' WHERE [index_symbol] = '{index_symbol}'"
        
        # Execute the SQL statement
        cursor.execute(script)
        return jsonify({'success': True}), 200
    except:
        return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

