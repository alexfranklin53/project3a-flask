from flask import Flask, render_template, request, url_for, flash, redirect, abort, session
from StockService import StockService
from StockChart import StockChart
from datetime import datetime
from StockLoader import StockLoader

app = Flask(__name__)
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = 'your secret key'
app.api_key = 'IKEQST513BE2TJ7E'
app.stocks = []
app.timeseries = ['Intraday', 'Daily', 'Weekly', 'Monthly']
app.charts = ['Bar', 'Line']

@app.before_request
def get_stock_data():
    app.stocks = StockLoader("stocks.csv").stocks

@app.route('/', methods=('GET', 'POST'))
def index():
    chart = None

    if request.method == 'POST':
        symbol = request.form['symbol']
        chart_type = request.form['chart_type']
        time_series_type = request.form['time_series_type']
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        session['symbol'] = symbol
        session['chart_type'] = chart_type
        session['time_series_type'] = time_series_type
        session['start_date'] = start_date
        session['end_date'] = end_date

        if check_inputs(symbol, chart_type, time_series_type, start_date, end_date):
            try:
                stock_service = StockService(app.api_key)
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

                time_series = stock_service.get_timeseries(time_series_type, symbol, start_date, end_date)
                chart_service = StockChart()
                chart = chart_service.graphData(chart_type, time_series)

                session.clear()
            except Exception as ex:
                flash(str(ex))
                return redirect(url_for('index'))
    return render_template('index.html', stocks=app.stocks, charts=app.charts, timeseries=app.timeseries, chart=chart)

def check_inputs(symbol, chart_type, time_series_type, start_date, end_date):
    valid = True
    if not symbol or symbol not in [stock.symbol for stock in app.stocks]:
        flash('Must have symbol')
        valid = False
    if not chart_type or chart_type not in app.charts:
        flash("Must have chart type")
        valid = False
    if not time_series_type or time_series_type not in app.timeseries:
        flash('Must have time series')
        valid = False
    if not start_date or not end_date:
        flash('Must have a start and end date')
        valid = False
    return valid

app.run(host="0.0.0.0", port=5001)