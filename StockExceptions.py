# Add custom exceptions here

class StockEndpointException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)

class StockLoaderException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)

class StockChartException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)

class StockQueryException(Exception):
    def __init__(self, msg):
        self.message = msg
        super().__init__(self.message)

class StockQueryLimitException(StockQueryException):
    def __init__(self):
        super().__init__("API limit reached. If you are using intraday, try a data set that is smaller than 5 months.")