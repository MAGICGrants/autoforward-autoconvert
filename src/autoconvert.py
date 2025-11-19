import math
import traceback
import random
import time
import util
import env


def get_balance(kraken_ticker):
    balances = util.kraken_request('/0/private/Balance')
    balance = 0
    if f'{kraken_ticker}' in balances:
        balance = float(balances[f'{kraken_ticker}'])
    return balance


def get_pair_details(quote_curency, base_currency, base_kraken_ticker):
    response = util.kraken_request('/0/public/AssetPairs', {'pair': f'{quote_curency}{base_currency}'})[f'{quote_curency}{base_kraken_ticker}']
    order_min = float(response['ordermin'])
    trade_decimals = int(response['pair_decimals'])
    return order_min, trade_decimals


def prepare_and_make_trade(balance, quote_currency, base_currency, base_kraken_ticker, payload):
    # Get trading pair details for a direct conversion
    order_min, trade_decimals = get_pair_details(quote_currency, base_currency, base_kraken_ticker)

    # If we continue, then we got the order_min and trade_decimals for the pair without issues
    # We ensure we have more than the minimum to trade
    if balance > order_min:
        # We get the current orderbook to calculate the mid market price
        orderbook = util.kraken_request('/0/public/Depth?count=1', {'pair': f'{quote_currency}{base_currency}'})[f'{quote_currency}{base_kraken_ticker}']

        # We make the trade
        mid_market_price = float(orderbook['bids'][0][0]) + ((float(orderbook['asks'][0][0]) - float(orderbook['bids'][0][0])) / 2) # Example 212.55+((212.72-212.55)/2) = 212.635
        limit_price = mid_market_price * (1-env.MAX_SLIPPAGE_PERCENT/100) # Example 212.365*(1-0.5/100) = 211.303175
        limit_price = round(limit_price, trade_decimals)  # Example 211.303175 -> 211.30
        payload['price'] = limit_price
        util.kraken_request('/0/private/AddOrder', payload)
        print(util.get_time(), f'Selling up to {balance} {quote_currency if payload["type"] == "sell" else base_currency} for pair {payload['pair']} for limit price {limit_price}')
    else:
        print(f'{quote_currency} balance {balance} is below the minimum of {order_min}; skipping')


def attempt_sell(asset, settlement_currency, settlement_kraken_ticker):
    payload = {
        'ordertype': 'limit',
        'timeinforce': 'IOC' # Immediately fill order to extent possible, then cancel
    }
    # First, check to see if the asset has a nonzero balance
    balance = get_balance(f'X{asset}')
    if balance > 0:
        try:
            payload['type'] = 'sell'
            payload['pair'] = f'{asset}{settlement_currency}'
            payload['volume'] = balance
            prepare_and_make_trade(balance, asset, settlement_currency, settlement_kraken_ticker, payload)
        except:
            # If we are here, then there is an issue getting the pair details and executing the trade
            # Either there is a Kraken error, or this trading pair does not exist
            print(f'Attempting to sell indirectly via other assets')
            for intermediary_currency, intermediary_kraken_ticker in [('USD', 'ZUSD'), ('USDT', 'USDT'), ('USDC', 'USDC'), ('EUR', 'ZEUR'), ('XBT', 'XXBT')]:
                # NOTE: it's possible for the conversion to be "stuck" in the intermediary currency if there is not enough to convert out of
                # Remove any intermediary currencies that you don't want value to get potentially stuck in
                # Conversion fees apply: https://www.kraken.com/features/fee-schedule#spot-crypto
                # Fees are lower for trades between stablecoins/FX, such as USDT/EUR
                try:
                    get_pair_details(asset, intermediary_currency, intermediary_kraken_ticker)  # Using asset as quote currency and intermediary as base currency
                    get_pair_details(settlement_currency, intermediary_currency, intermediary_kraken_ticker)  # Using settlement currency as quote currency and intermediary as base currency
                    # If we made it here, then a route through the intermediary currency exists (we would have gotten an error with get_pair_details if it didn't)
                    # Start the first trade, selling the asset for the base intermediary currency
                    payload['type'] = 'sell'
                    payload['pair'] = f'{asset}{intermediary_currency}'
                    payload['volume'] = balance
                    prepare_and_make_trade(balance, asset, intermediary_currency, intermediary_kraken_ticker, payload)
                    intermediary_balance = get_balance(intermediary_currency)
                    # Start the second trade, buying the quote settlement currency with the base intermediary currency balance
                    payload['type'] = 'buy'
                    payload['pair'] = f'{settlement_currency}{intermediary_currency}'
                    payload['volume'] = intermediary_balance
                    prepare_and_make_trade(balance, intermediary_kraken_ticker)
                except:
                    print(f'No path found through {intermediary_currency}')
                    continue
    else:
        print(f'No balance for {asset}; skipping')

if __name__ == '__main__':
    if env.TESTNET == '1':
        print('Testnet mode enabled. Autoconvert will now sleep forever. Zz Zz Zz...')
        time.sleep(999999999)

    while 1:
        # First, get the settlement currency formatted correctly
        settlement_currency = env.SETTLEMENT_CURRENCY
        # https://support.kraken.com/hc/en-us/articles/360001206766-Bitcoin-currency-code-XBT-vs-BTC
        if settlement_currency in ['AUD', 'CAD', 'EUR', 'GBP', 'JPY', 'USD']:
            settlement_kraken_ticker = 'Z' + settlement_currency
        elif settlement_currency in ['ETC', 'ETH', 'LTC', 'MLN', 'REP', 'XBT', 'XDG', 'XLM', 'XMR', 'XRP', 'ZEC']:
            settlement_kraken_ticker = 'X' + settlement_currency
        else:
            settlement_kraken_ticker = settlement_currency

        # Then, initiate the selling process for each supported asset unless it's already the settlement currency
        for asset in ['XBT', 'LTC', 'XMR']:
            try:
                if settlement_currency != asset:
                    attempt_sell(asset, settlement_currency, settlement_kraken_ticker)
                else:
                    print(f'Not converting {asset} since it is already in the settlement currency')
            except Exception as e:
                print(util.get_time(), f'Error attempting to sell {asset}:')
                print(traceback.format_exc())

        delay = random.randint(30, 90)
        time.sleep(delay)
