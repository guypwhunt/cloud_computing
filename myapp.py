# Import the necessary libraries
from flask import Flask, jsonify, request, render_template
import mysql.connector
import requests
import requests_cache
import json
import collections

# Libraries that are no longer needed
#import jwt
#import pandas as pd

requests_cache.install_cache('index_api_cache', backend='sqlite', expire_after=36000)

app = Flask(__name__)

# Define the connection parameters for the SQL database
"""mydb = mysql.connector.connect(
  host="investment.cgwmqkwedlgo.us-east-1.rds.amazonaws.com",
  user="Rafayet",
  password="Cloud2021",
  database="Invest"
)"""

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
<b>Get index information</b>
<p>Request type: GET</p>
<p>Path: /indexes/stock_data/"symbol"/"function"</p>
<p>Index Price Time Series Function Options: TIME_SERIES_INTRADAY, TIME_SERIES_DAILY, TIME_SERIES_WEEKLY, TIME_SERIES_MONTHLY</p>
<p>Index Fundamental Information Function Options: OVERVIEW, EARNINGS, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW, LISTING_STATUS, EARNINGS_CALENDAR, IPO_CALENDAR</p>
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

"""# Get Request
@app.route('/indexes/', methods=['GET'])
def get_indexes():
    # This function gets all the indexes in the database
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Perform the select statement and extract the rows
        mycursor.execute("select * from index_data")
        rows = mycursor.fetchall()

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
        #response = jwt.encode(response, 'secret', algorithm='HS256')
        return(response),200
    except:
        return jsonify({'error':'there was an error getting the indexes'}), 400

# Get Request
@app.route('/indexes/<symbol>', methods=['GET'])
def get_index(symbol):
    # This function gets a specific index from the database
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Perform the select statement and extract the rows for the index
        sql_script = 'SELECT * FROM index_data WHERE index_symbol = \'' + symbol + '\''
        
        mycursor.execute(sql_script)
        rows = mycursor.fetchall()
        
        # Respond with an error if no rows were obtained from the SQL query
        if rows == []:
            return jsonify({'error':'the index does not exist'}), 404
        else:        
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
        return jsonify({'error':'there was an error getting the index'}), 400
        
    
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
        return jsonify({'error':'there was an error getting the ' + symbol +' stock data'}), 400

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
        mycursor = mydb.cursor()
        
        # Define input variables
        pk_index_id = request.json['pk_index_id']
        index_name = request.json['index_name']
        index_symbol = request.json['index_symbol']
        pk_index_id = str(pk_index_id)
        
        # Create the appropriate SQL script
        sql = "INSERT INTO index_data (pk_index_id, index_name, index_symbol) VALUES (%s, %s, %s)"
        val = (pk_index_id, index_name, index_symbol)

        # Execute the SQL statement
        mycursor.execute(sql, val)
        mydb.commit()
        return jsonify({'message':'new index created: {}'.format([index_name])}), 201
    except:
        return jsonify({'error':'there was an error adding the index'}), 400


# Delete Request
@app.route('/indexes/delete_index/<index_symbol>', methods=['DELETE'])
def delete_index(index_symbol):
    # This function allows user to delete an index
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Create the appropriate SQL script
        script = 'DELETE FROM index_data WHERE index_symbol = \''+index_symbol+'\''

        # Execute the SQL statement
        mycursor.execute(script)
        mydb.commit()
        
        # Respond with error if no rows were deleted
        if mycursor.rowcount == 0:
            return jsonify({'error':'the index does not exist'}), 404
        else:
            row_count = (mycursor.rowcount, "record(s) affected")
            return jsonify({'success': True, 'rows affected': row_count[0]}), 200
    except:
        return jsonify({'success': False}), 400

# Put Request
@app.route('/indexes/update_index/<index_symbol>', methods=['PUT'])
def update_index(index_symbol):
    # This function allows users to update an index
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Identify if the body contains all the necessary data
        if not request.json or not 'pk_index_id' in request.json:
            return jsonify({'error':'the updated index needs to have a pk_index_id'}), 400
        if not request.json or not 'index_name' in request.json:
            return jsonify({'error':'the updated index needs to have a index_name'}), 400
        
        # Define input variables
        pk_index_id = request.json['pk_index_id']
        index_name = request.json['index_name']
        pk_index_id = str(pk_index_id)

        # Create the appropriate SQL script
        script = 'UPDATE index_data SET pk_index_id = \''+ pk_index_id + '\', index_name = \'' + index_name + '\' WHERE index_symbol = \'' + index_symbol + '\''
        
        # Execute the SQL statement
        mycursor.execute(script)
        mydb.commit()
        
        # Respond with error if no rows were updated
        if mycursor.rowcount == 0:
            return jsonify({'error':'the index does not exist'}), 404
        else:
            row_count = (mycursor.rowcount, "record(s) affected")
            return jsonify({'success': True, 'rows affected': row_count[0]}), 200
    except:
        return jsonify({'success': False}), 400"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
