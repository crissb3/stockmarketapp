import datetime
import os
import logging
import time
import pyodbc
import requests
import azure.functions as func
import json

app = func.FunctionApp()


def fetch_latest_prices(symbol: str, api_key: str, is_crypto: bool = False):
    if is_crypto:
        url = ('https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE'
               f'&from_currency={symbol}&to_currency=EUR&apikey={api_key}'
        )
        key_name = "Realtime Currency Exchange Rate"
    else:
        url = ("https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY"
               f"&symbol={symbol}&interval=60min&apikey={api_key}"
        )
        key_name = "Time Series (60min)"

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        data = r.json()

        if key_name in data:
            daily_data = data[key_name]
            latest_datetime = daily_data["6. Last Refreshed"] if is_crypto else next(iter(daily_data))
            latest_close = float(daily_data["5. Exchange Rate"]) if is_crypto else float(daily_data[latest_datetime]["4. close"])
            return {
                "symbol": symbol,
                "datetime": latest_datetime,
                "latest_close": latest_close
            }

        elif "Information" in data:
            logging.info(data)
        else:
            logging.error(f"Unexpected response: {data}")

    except Exception as e:
        logging.error(e)

    return None


def save_to_db(total_value_nok, results):
    today = datetime.datetime.now()
    try:
        cnxn = pyodbc.connect(os.environ['CONNECTION_STRING'])
        cursor = cnxn.cursor()
        for symbol, data in results.items():
            cursor.execute("""
                           INSERT INTO AssetHistory (datetime, symbol, latest_close, shares, value, currency)
                           VALUES (?, ?, ?, ?, ?, ?)
                           """, (
                               data["datetime"],
                               symbol,
                               data["latest_close"],
                               data["shares"],
                               data["value"],
                               data["currency"]
                           ))
        cursor.execute("""
                       INSERT INTO PortfolioTotals (datetime, currency, total_value)
                       VALUES (?, ?, ?)
                       """, (
            today,
            "NOK",
            total_value_nok
        ))

        cnxn.commit()
        cursor.close()
        cnxn.close()
    except pyodbc.Error as e:
        sqlstate = e.args[0]  # sqlstate error code
        logging.error(sqlstate)
        raise


@app.timer_trigger(schedule="0 0 16 * * *", arg_name="myTimer", use_monitor=True)
def timer_trigger1(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")


    nasdaq_tickers = ["MAXN", "NVDA", "PANW", "TTD"]
    crypto_tickers = ["BTC", "ETH", "LINK", "SOL", "DOT"]
    api_key = os.environ["ALPHAVANTAGE_KEY"]

    results = {}
    my_holdings = {
        "MAXN": 100,
        "NVDA": 1,
        "PANW": 1,
        "TTD": 1,
        "BTC": 0.01,
        "ETH": 0.1,
        "LINK": 10,
        "SOL": 1,
        "DOT": 100,
    }

    for symbol in nasdaq_tickers + crypto_tickers:
        is_crypto = symbol in crypto_tickers
        latest_prices = fetch_latest_prices(symbol, api_key, is_crypto=(is_crypto))
        if latest_prices:
            shares = my_holdings.get(symbol, 0)
            latest_prices["shares"] = shares
            latest_prices["currency"] = "EUR" if is_crypto else "USD"
            latest_prices["value"] = round(latest_prices["latest_close"] * my_holdings[symbol], 2)
            results[symbol] = latest_prices
        time.sleep(15) # Only 5 calls per minute on free tier for Alpha Vantage. Adding sleep for 15s not to go past this limit.



    if results:
        portfolio_totals = {
            "USD": 0,
            "EUR": 0
        }
        for data in results.values():
            portfolio_totals[data["currency"]] += data["value"]

        exchange_rates = {}
        for key in portfolio_totals:
            try:
                url = ('https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE'
                       f'&from_currency={key}&to_currency=NOK&apikey={api_key}'
                )
                r = requests.get(url, timeout=5)
                r.raise_for_status()
                data = r.json()

                if "Realtime Currency Exchange Rate" in data:
                    rate = float(data["Realtime Currency Exchange Rate"]["5. Exchange Rate"])
                    exchange_rates[key] = rate
                else:
                    logging.warning(f"No exchange rates found for {key}: {data}")
            except Exception as e:
                logging.error(e)
                exchange_rates[key] = 0
        total_value_nok = sum(
            portfolio_totals[currency] * exchange_rates.get(currency, 0)
            for currency in portfolio_totals
        )

        total_value_nok = round(total_value_nok, 2)
        logging.info(f"Total value in NOK: {total_value_nok}")
        logging.info(json.dumps(results, indent=2))

        save_to_db(total_value_nok, results)



# Displaye graf med gains/loss for dataen jeg har.
# Forbedring: Sjekke for dag i uka for å unngå å hente inn data for stocks dager markedet er nede (lør, søn). Kun hente cryptoverdier disse dagene og bruk siste innhentet data for stocks, for å oppdatere totalverdi på de dagene.