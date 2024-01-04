from datetime import datetime
from pandas_datareader import data as pdr
import yfinance as yf

yf.pdr_override()

# functions that the assistant can run, defined in assistant
# data is sourced with assistant definition and then passed back to the run in JSON

def stock_prices(tickers: str, start: str, end: str = None) -> str:
    '''
    Function to retrieve daily adjusted stock prices from an API
    Takes a list of tickers
    start and end times as strings
    returns a json format string of daily prices
    '''
    # get today's date if no end given
    if end == None:
        end = datetime.today().strftime("%Y-%m-%d")
    tickers = tickers.split(',')
    data = pdr.get_data_yahoo(tickers, start=start, end=end)
    
    return data['Adj Close'].to_json()