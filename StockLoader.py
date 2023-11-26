from Models import Stock
import csv
from StockExceptions import StockLoaderException

class StockLoader:
    def __init__(self, stocks_path):
        self.stocks_path = stocks_path
        self.stocks = self.load_stocks()

    def load_stocks(self):
        try:
            stocks = []
            with open(self.stocks_path, newline = '') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    stocks.append(Stock(row['Symbol'], row['Name'], row['Sector']))
            return stocks
        except Exception as ex:
            raise StockLoaderException(f"Error loading the stock data: {ex}")