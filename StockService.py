import requests
from datetime import datetime
# local imports
from Models import StockValue, TimeSeries
from Utility import Utility
from StockExceptions import StockQueryException, StockQueryLimitException, StockEndpointException

class StockService:
    BASE_URL = "https://www.alphavantage.co/query"
    INTRA_TYPE = "TIME_SERIES_INTRADAY"
    DAILY_TYPE = "TIME_SERIES_DAILY"
    WEEKLY_TYPE = "TIME_SERIES_WEEKLY"
    MONTHLY_TYPE = "TIME_SERIES_MONTHLY"
    INTRA_TIME_INTERVAL = "60min" #interval for intraday

    DEFAULT_OUTPUT_SIZE = "full" #default output size

    def __init__(self, api_key):
        self.api_key = api_key

    def __query_api(self, data_type: str, symbol: str, additional_params: dict = {}):
        params = {
            "function": data_type,
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": self.DEFAULT_OUTPUT_SIZE  # added default ouput size
        }
        params.update(additional_params)

        response = requests.get(self.BASE_URL, params=params)
        # ensure the request was successful
        if response.status_code != 200:
            raise StockEndpointException(response.text)
        # check for json errors / no response?
        if 'Error Message' in response.text:
            raise StockQueryException(response.text)
        # check for api limit reached
        if 'Thank you for using' in response.text or '**demo**' in response.text:
            raise StockQueryLimitException()
        return response.json()

    def __create_series_data(self, symbol: str, json_response, items_label: str) -> [StockValue]:
        """
        Create a TimeSeries instance from the JSON response from the API.
        """
        try:
            series_data = []
            for date, daily_data in json_response[items_label].items():
                stock_data = StockValue(
                    symbol=symbol,
                    date=date,
                    open=float(daily_data['1. open']),
                    high=float(daily_data['2. high']),
                    low=float(daily_data['3. low']),
                    close=float(daily_data['4. close']),
                    volume=int(daily_data['5. volume']),
                )
                series_data.append(stock_data)

            return series_data
        except KeyError:
            raise StockQueryException("API returned an unexpected response.")

    # Intraday is limited to a 1 month range, so we need to make multiple requests to get the full dataset
    def get_intraday(self, symbol: str, start_date: datetime, end_date: datetime) -> TimeSeries:
        months = Utility.get_months_between(start_date, end_date)
        series_data = []
        for month in months:
            res = self.__query_api(self.INTRA_TYPE, symbol, {"month": month.strftime('%Y-%m'), "interval": self.INTRA_TIME_INTERVAL})
            series_data += self.__create_series_data(symbol, res, 'Time Series (60min)')

        return TimeSeries(symbol, self.INTRA_TYPE, start_date, end_date, series_data)

    def get_daily(self, symbol: str, start_date: datetime, end_date: datetime) -> TimeSeries:
        res = self.__query_api(self.DAILY_TYPE, symbol)
        series_data = self.__create_series_data(symbol, res, 'Time Series (Daily)')
        return TimeSeries(symbol, self.DAILY_TYPE, start_date, end_date, series_data)

    
    def get_weekly(self, symbol: str, start_date: datetime, end_date: datetime) -> TimeSeries:
        res = self.__query_api(self.WEEKLY_TYPE, symbol)
        series_data = self.__create_series_data(symbol, res, 'Weekly Time Series')
        return TimeSeries(symbol, self.WEEKLY_TYPE, start_date, end_date, series_data)
    
    def get_monthly(self, symbol: str, start_date: datetime, end_date: datetime) -> TimeSeries:
        res = self.__query_api(self.MONTHLY_TYPE, symbol)
        series_data = self.__create_series_data(symbol, res, 'Monthly Time Series')
        return TimeSeries(symbol, self.MONTHLY_TYPE, start_date, end_date, series_data)

    def get_timeseries(self, series_type, symbol, start_date, end_date) -> TimeSeries:
        if series_type == 'Intraday':
            return self.get_intraday(symbol, start_date, end_date)
        elif series_type == 'Daily':
            return self.get_daily(symbol, start_date, end_date)
        elif series_type == 'Weekly':
            return self.get_weekly(symbol, start_date, end_date)
        elif series_type == 'Monthly':
            return self.get_monthly(symbol, start_date, end_date)
        else:
            raise StockQueryException(f"Invalid series type: {series_type}")