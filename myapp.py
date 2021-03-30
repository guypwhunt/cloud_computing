# Import the necessary libraries
from flask import Flask, jsonify, request, render_template
import mysql.connector
import requests
import json
import collections

# Libraries that are no longer needed
#import jwt
#import pandas as pd

app = Flask(__name__)

# This allows for testing when the database is turned off
try:
    # Define the connection parameters for the SQL database
    mydb = mysql.connector.connect(
    host="investment.cgwmqkwedlgo.us-east-1.rds.amazonaws.com",
    user="Rafayet",
    password="Cloud2021",
    database="Invest"
    )
except:
    x=1


@app.route('/')
def api_information():
    # This function returns a HTML page with information on all the other APIs
    return """<html>
<body>
<h1>Investment Restful API Service</h1>
<h3>Designed, developed and implemented by Shabnam Manjuri, Rafayet Tarafder, Rohit Garg, Helen Louise Gaden and Guy Hunt</h3>
<b>Group: 11</b>
<br></br>
<br></br>
<b>Get all the stocks</b>
<p>Request type: GET</p>
<p>Path: /stocks/</p>
<br></br>
<b>Get a specific stock</b>
<p>Request type: GET</p>
<p>Path: /stocks/"symbol"</p>
<p>Example Path: /stocks/AMZN</p>
<br></br>
<b>Search for stock symbol</b>
<p>Request type: GET</p>
<p>Path: /stocks/search/"stock_name"</p>
<p>Example Path: /stocks/search/Microsoft</p>
<br></br>
<b>Get stock information</b>
<p>Request type: GET</p>
<p>Path: /stocks/stock_data/"symbol"/"function"</p>
<p>Stock Price Time Series Function Options: TIME_SERIES_INTRADAY, TIME_SERIES_DAILY, TIME_SERIES_WEEKLY, TIME_SERIES_MONTHLY</p>
<p>Stock Fundamental Information Function Options: OVERVIEW, EARNINGS, INCOME_STATEMENT, BALANCE_SHEET, CASH_FLOW, LISTING_STATUS, EARNINGS_CALENDAR, IPO_CALENDAR</p>
<p>Example Path: /stocks/stock_data/AMZN/TIME_SERIES_MONTHLY</p>
<br></br>
<b>Add new stock</b>
<p>Request type: POST</p>
<p>Path: /stocks/add_stock</p>
<p>Example Body: {"pk_stock_id": 10,
    "stock_name": "TEST STOCK",
    "stock_symbol": "TEST"}</p>
<br></br>
<b>Update stock</b>
<p>Request type: PUT</p>
<p>Path: /stocks/update_stock/"symbol"</p>
<p>Example Body: {
    "pk_stock_id": "10",
    "stock_name": "TEST STOCK 2"
}</p>
<br></br>
<b>Delete stock</b>
<p>Request type: DELETE</p>
<p>Path: /stocks/delete_stock/"symbol"</p>
<br></br>
</body>
</html>"""

# Get Request
@app.route('/stocks/', methods=['GET'])
def get_stocks():
    # This function gets all the stocks in the database
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Perform the select statement and extract the rows
        mycursor.execute("select * from stock_data")
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
            d["stock_id"] = row[0]
            d["stock_name"] = row[1]
            d["stock_symbol"] = row[2]
            objects_list.append(d)
        
        # Convert key-value pairs to JSON
        response = json.dumps(objects_list)
        #response = jwt.encode(response, 'secret', algorithm='HS256')
        return(response),200
    except:
        return jsonify({'error':'there was an error getting the stocks'}), 400

# Get Request
@app.route('/stocks/<symbol>', methods=['GET'])
def get_stock(symbol):
    # This function gets a specific stock from the database
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Perform the select statement and extract the rows for the stock
        sql_script = 'SELECT * FROM stock_data WHERE stock_symbol = \'' + symbol + '\''
        
        mycursor.execute(sql_script)
        rows = mycursor.fetchall()
        
        # Respond with an error if no rows were obtained from the SQL query
        if rows == []:
            return jsonify({'error':'the stock does not exist'}), 404
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
                d["stock_id"] = row[0]
                d["stock_name"] = row[1]
                d["stock_symbol"] = row[2]
                objects_list.append(d)

            # Convert key-value pairs to JSON
            response = json.dumps(objects_list)
            return(response),200
    except:
        return jsonify({'error':'there was an error getting the stock'}), 400
        
    
# External API Request
@app.route('/stocks/search/<stock_name>', methods=['GET'])
def get_search_stock(stock_name):
    # This function gets the stocks symbol and basic information
    try:
        # Define the non-variable API parameters 
        ploads = {'datatype': 'json', 'apikey': '5VKW15ETPEN1FRNO', 'function': 'SYMBOL_SEARCH'}
        url = 'https://www.alphavantage.co/query?'

        # Update the variable parameters
        ploads['keywords'] = stock_name
        
        # Make the get equest
        response = requests.get(url, params=ploads)

        return(json.loads(response.text)),200
    except:
        return jsonify({'error':'there was an error getting the ' + symbol +' information'}), 400
        
# External API Request
@app.route('/stocks/stock_data/<symbol>/<function>', methods=['GET'])
def get_stock_time_series(symbol, function):
    # This function gets the stocks stock price time series data
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
@app.route('/stocks/add_stock', methods=['POST'])
def create_an_stock():
    # This function allows users to add an stock to the database
    try:
        # Identify if the body contains all the necessary data
        if not request.json or not 'pk_stock_id' in request.json:
            return jsonify({'error':'the new stock needs to have a pk_stock_id'}), 400
        if not request.json or not 'stock_name' in request.json:
            return jsonify({'error':'the new stock needs to have a stock_name'}), 400
        if not request.json or not 'stock_symbol' in request.json:
            return jsonify({'error':'the new stock needs to have a stock_symbol'}), 400

        # Open a connection to the database
        mycursor = mydb.cursor()
        
        # Define input variables
        pk_stock_id = request.json['pk_stock_id']
        stock_name = request.json['stock_name']
        stock_symbol = request.json['stock_symbol']
        pk_stock_id = str(pk_stock_id)
        
        # Create the appropriate SQL script
        sql = "INSERT INTO stock_data (pk_stock_id, stock_name, stock_symbol) VALUES (%s, %s, %s)"
        val = (pk_stock_id, stock_name, stock_symbol)

        # Execute the SQL statement
        mycursor.execute(sql, val)
        mydb.commit()
        return jsonify({'message':'new stock created: {}'.format([stock_name])}), 201
    except:
        return jsonify({'error':'there was an error adding the stock'}), 400


# Delete Request
@app.route('/stocks/delete_stock/<symbol>', methods=['DELETE'])
def delete_stock(symbol):
    # This function allows user to delete an stock
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Create the appropriate SQL script
        script = 'DELETE FROM stock_data WHERE stock_symbol = \''+symbol+'\''

        # Execute the SQL statement
        mycursor.execute(script)
        mydb.commit()
        
        # Respond with error if no rows were deleted
        if mycursor.rowcount == 0:
            return jsonify({'error':'the stock does not exist'}), 404
        else:
            row_count = (mycursor.rowcount, "record(s) affected")
            return jsonify({'success': True, 'rows affected': row_count[0]}), 200
    except:
        return jsonify({'success': False}), 400

# Put Request
@app.route('/stocks/update_stock/<symbol>', methods=['PUT'])
def update_stock(symbol):
    # This function allows users to update an stock
    try:
        # Open a connection to the database
        mycursor = mydb.cursor()

        # Identify if the body contains all the necessary data
        if not request.json or not 'pk_stock_id' in request.json:
            return jsonify({'error':'the updated stock needs to have a pk_stock_id'}), 400
        if not request.json or not 'stock_name' in request.json:
            return jsonify({'error':'the updated stock needs to have a stock_name'}), 400
        
        # Define input variables
        pk_stock_id = request.json['pk_stock_id']
        stock_name = request.json['stock_name']
        pk_stock_id = str(pk_stock_id)

        # Create the appropriate SQL script
        script = 'UPDATE stock_data SET pk_stock_id = \''+ pk_stock_id + '\', stock_name = \'' + stock_name + '\' WHERE stock_symbol = \'' + symbol + '\''
        
        # Execute the SQL statement
        mycursor.execute(script)
        mydb.commit()
        
        # Respond with error if no rows were updated
        if mycursor.rowcount == 0:
            return jsonify({'error':'the stock does not exist'}), 404
        else:
            row_count = (mycursor.rowcount, "record(s) affected")
            return jsonify({'success': True, 'rows affected': row_count[0]}), 200
    except:
        return jsonify({'success': False}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
