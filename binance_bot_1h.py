import pandas as pd
from datetime import datetime
import ccxt
from binance.client import Client
import pandas_ta as ta
from ta.trend import EMAIndicator
import smtplib
import numpy as np

api_key = 'vBNkUMfiZAGRB2st3xthbEhxWwHqPCsxaXVbKXxgFZYytMnTrNWiQEHssX7aNk9t'
api_secret = '2c0Ro00uywRedgEPjiYx91eSoj5pzaZGrZWapBx66kqZfM1NnJfTcYze26oyYYBk'

client = ccxt.binance({"apiKey": api_key,"secret": api_secret,'options': 
{'defaultType': 'future'},'enableRateLimit': True})
client_b = Client(api_key, api_secret, {"timeout": 60})

leverage =10

lista_1 = ['ADAUSDT', 'MATICUSDT', 'DOGEUSDT', 'DOTUSDT', 'SOLUSDT']

timestamp_today = 0
fecha_test = 0
fecha_test_1 = 0
lista = []
for x in lista_1:
    get_open_order = client_b.futures_position_information(symbol = x)[0]['symbol']
    if x == get_open_order:
        lista.append(x)

print('Estoy en la nube')

while True:
    try:

        account_info = client_b.futures_account_balance()

        for info in range(0, len(account_info), 1):
    
                if account_info[info]['asset'] == 'USDT':

                    balance = (float(account_info[info]['balance'])/0.11)
                    #cantidad_usd = round(balance,2)  
                    cantidad_usd = balance
                    cantidad_limite = 1.3*cantidad_usd/10
        
        for COIN in lista:


            get_open_order = client_b.futures_position_information()

            for x in range(0, len(get_open_order), 1):

                get_open_order = client_b.futures_position_information()
                notional = float(get_open_order[x]['notional'])
                

                if notional != 0 : 
                    
                    COIN_o = get_open_order[x]['symbol']

                    bars = client.fetch_ohlcv(COIN_o, timeframe='1h', since = None, limit = 1500)
                    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
                    df["timestamp"] = [datetime.fromtimestamp(x) for x in df["timestamp"]/1000]

                    n = 14

                    def rma(x, n, y0):
                        a = (n-1) / n
                        ak = a**np.arange(len(x)-1, -1, -1)
                        return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

                    df['change'] = df['close'].diff()
                    df['gain'] = df.change.mask(df.change < 0, 0.0)
                    df['loss'] = -df.change.mask(df.change > 0, -0.0)
                    df['avg_gain'] = rma(df.gain[n+1:].to_numpy(), 14, np.nansum(df.gain.to_numpy()[:14+1])/14)
                    df['avg_loss'] = rma(df.loss[n+1:].to_numpy(), 14, np.nansum(df.loss.to_numpy()[:14+1])/14)
                    df['rs'] = df.avg_gain / df.avg_loss
                    df['rsi_14'] = 100 - (100 / (1 + df.rs))

                    Last_signal_1 = len(df)-1

                    get_open_order = client_b.futures_position_information(symbol = COIN)
                    value = float(get_open_order[0]['notional'])

                    if value > 0 and df['rsi_14'][Last_signal_1] > 70:

                        get_open_order = client_b.futures_position_information(symbol = COIN)
                        value = float(get_open_order[0]['notional'])
                        cantidad_ro = abs(float(get_open_order[0]['positionAmt']))*2
                                        
                        close_position_buy = client_b.futures_create_order(symbol= COIN,side='SELL',
                        type="MARKET", quantity=cantidad_ro, reduceOnly='true')
                    
                        date_today = datetime.today()
                        timestamp_today = datetime.timestamp(date_today)

                        print('se cerro orden de compra por RSI, '+str(datetime.today()))
                        fecha_test = df['timestamp'][Last_signal_1]
                        print(fecha_test)
            
                    if value < 0 and df['rsi_14'][Last_signal_1] < 30:

                        get_open_order = client_b.futures_position_information(symbol = COIN)
                        value = float(get_open_order[0]['notional'])
                        cantidad_ro = abs(float(get_open_order[0]['positionAmt']))*2
                    
                        close_position_sell = client_b.futures_create_order(symbol=COIN,side='BUY',
                        type="MARKET", quantity=cantidad_ro, reduceOnly='true')
            
                        date_today = datetime.today()
                        timestamp_today = datetime.timestamp(date_today)

                        print('se cerro orden de venta por RSI, '+str(datetime.today()))
                        fecha_test = df['timestamp'][Last_signal_1]
                        print(fecha_test)   
                    
                    continue
    
                else:

                    get_open_order = client_b.futures_position_information()

                    get_open_order = client_b.futures_position_information(symbol = COIN)[0]['symbol']

                    if get_open_order == COIN:

                        leverage = client_b.futures_change_leverage(symbol=COIN, leverage=10)

                        bars = client.fetch_ohlcv(lista[0], timeframe='1h', since = None, limit = 1500)
                        df_1h = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
                        last_date = df_1h['timestamp'].tail(1)
                        first_date = df_1h['timestamp'].head(1)
                        df_1h["timestamp"] = [datetime.fromtimestamp(x) for x in df_1h["timestamp"]/1000]

                        Ema_12 = EMAIndicator(df_1h["close"], float(12))
                        df_1h["EMA_12"] = Ema_12.ema_indicator()

                        Ema_26 = EMAIndicator(df_1h["close"], float(26))
                        df_1h["EMA_26"] = Ema_26.ema_indicator()

                        df_1h.ta.sma(length=50, append=True)
                        df_1h.ta.sma(length=200, append=True)

                        #####################################################  6 HORAS ############################################################

                        bars = client.fetch_ohlcv(lista[0], timeframe='6h', since = None, limit = 1500)
                        df_6h = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
                        last_date = df_6h['timestamp'].tail(1)
                        first_date = df_6h['timestamp'].head(1)
                        df_6h["timestamp"] = [datetime.fromtimestamp(x) for x in df_6h["timestamp"]/1000]

                        Ema_12 = EMAIndicator(df_6h["close"], float(12))
                        df_6h["EMA_12"] = Ema_12.ema_indicator()

                        Ema_26 = EMAIndicator(df_6h["close"], float(26))
                        df_6h["EMA_26"] = Ema_26.ema_indicator()

                        df_6h.ta.sma(length=50, append=True)
                        df_6h.ta.sma(length=200, append=True)

                        EMA_12_6H = df_6h['EMA_12'].iloc[-1]
                        EMA_26_6H = df_6h['EMA_26'].iloc[-1]
                        EMA_12_1H = df_1h['EMA_12'].iloc[-1]
                        EMA_26_1H = df_1h['EMA_26'].iloc[-1]

                        Caso_15min = 0
                        Caso_1h = 0

                        if EMA_12_6H > EMA_26_6H and EMA_12_1H > EMA_26_1H:
                            
                            print("Ir a los 15 min")
                            Caso_15min = '15m'
                            
                        if EMA_12_6H < EMA_26_6H and EMA_12_1H < EMA_26_1H:
                            
                            print("Ir a 1 h")
                            Caso_1h = '1h'

                        df = pd.DataFrame()

                        if Caso_1h == '1h':
                            
                            bars = client.fetch_ohlcv(lista[0], timeframe='1h', since = None, limit = 1500)
                            df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
                            last_date = df['timestamp'].tail(1)
                            first_date = df['timestamp'].head(1)
                            df["timestamp"] = [datetime.fromtimestamp(x) for x in df["timestamp"]/1000]

                            Ema_12 = EMAIndicator(df["close"], float(12))
                            df["EMA_12"] = Ema_12.ema_indicator()

                            Ema_26 = EMAIndicator(df["close"], float(26))
                            df["EMA_26"] = Ema_26.ema_indicator()

                            df.ta.sma(length=50, append=True)
                            df.ta.sma(length=200, append=True)
                            
                            macd_1h = df.ta.macd(close='close', fast=12, slow=26, signal=9, append=True)
                            
                            df['Order_macd'] = 0
                            df.loc[(df['MACD_12_26_9'] > df['MACDs_12_26_9']), 'Order_macd'] = 'BUY'
                            df.loc[(df['MACD_12_26_9'] < df['MACDs_12_26_9']), 'Order_macd'] = 'SELL'
                            
                            n = 14

                            def rma(x, n, y0):
                                a = (n-1) / n
                                ak = a**np.arange(len(x)-1, -1, -1)
                                return np.r_[np.full(n, np.nan), y0, np.cumsum(ak * x) / ak / n + y0 * a**np.arange(1, len(x)+1)]

                            df['change'] = df['close'].diff()
                            df['gain'] = df.change.mask(df.change < 0, 0.0)
                            df['loss'] = -df.change.mask(df.change > 0, -0.0)
                            df['avg_gain'] = rma(df.gain[n+1:].to_numpy(), 14, np.nansum(df.gain.to_numpy()[:14+1])/14)
                            df['avg_loss'] = rma(df.loss[n+1:].to_numpy(), 14, np.nansum(df.loss.to_numpy()[:14+1])/14)
                            df['rs'] = df.avg_gain / df.avg_loss
                            df['rsi_14'] = 100 - (100 / (1 + df.rs))
                            
                            df['Order_ema'] = 0
                            df.loc[(df['EMA_12'] > df['EMA_26']), 'Order_ema'] = 'BUY'
                            df.loc[(df['EMA_12'] < df['EMA_26']), 'Order_ema'] = 'SELL'
                            
                            df['Trend'] = 0
                            df.loc[(df['SMA_50'] > df['SMA_200']), 'Trend'] = 'BUY_trend'
                            df.loc[(df['SMA_50'] < df['SMA_200']), 'Trend'] = 'SELL_trend'

                            df.ta.eri(append=True)
                            df['SUMA_ERI'] = df['BULLP_13'] + df['BEARP_13']
                            
                            df['ERI'] = 0
                            df.loc[(df['SUMA_ERI'] > 0), 'ERI'] = 'BUY'
                            df.loc[(df['SUMA_ERI'] < 0), 'ERI'] = 'SELL'

                            df['Signal'] = 0
                            df.loc[(df['Order_ema'] == 'BUY') & (df['Order_macd'] == 'BUY'), 'Signal'] = 'BUY'
                            df.loc[(df['Order_ema'] == 'SELL') & (df['Order_macd'] == 'SELL'), 'Signal'] = 'SELL'
                            
                            df['match'] = df['Signal'] == df['Signal'].shift()
                            df.loc[(df['Signal'] == 0 ) , 'match'] = True

                            df.loc[df['match'] == False, 'SEÑAL'] = 1
                            df.loc[df['match'] == True, 'SEÑAL'] = 0

                        if len(df) == 0:

                            continue

                        Last_signal_1 = len(df)-2
                        
                        get_open_order = client_b.futures_position_information(symbol = COIN)
                        value = float(get_open_order[0]['notional'])

                        account_info = client_b.futures_account()

                        if value != 0 :

                            get_open_order = client_b.futures_position_information(symbol = COIN)
                            value = float(get_open_order[0]['notional'])

                            if value > 0 and df['Signal'][Last_signal_1] == 'SELL':

                                get_open_order = client_b.futures_position_information(symbol = COIN)
                                value = float(get_open_order[0]['notional'])
                                cantidad_ro = abs(float(get_open_order[0]['positionAmt']))*2
                                                
                                close_position_buy = client_b.futures_create_order(symbol= COIN,side='SELL',
                                type="MARKET", quantity=cantidad_ro, reduceOnly='true')
                            
                                date_today = datetime.today()
                                timestamp_today = datetime.timestamp(date_today)

                                print('se cerro orden de compra por cambio de señal a SELL, '+str(datetime.today()))
                                fecha_test = df['timestamp'][Last_signal_1]
                                print(fecha_test)
                    
                            if value < 0 and df['Signal'][Last_signal_1] == 'BUY':

                                get_open_order = client_b.futures_position_information(symbol = COIN)
                                value = float(get_open_order[0]['notional'])
                                cantidad_ro = abs(float(get_open_order[0]['positionAmt']))*2
                            
                                close_position_sell = client_b.futures_create_order(symbol=COIN,side='BUY',
                                type="MARKET", quantity=cantidad_ro, reduceOnly='true')
                    
                                date_today = datetime.today()
                                timestamp_today = datetime.timestamp(date_today)

                                print('se cerro orden de venta por cambio de señal a buy, '+str(datetime.today()))
                                fecha_test = df['timestamp'][Last_signal_1]
                                print(fecha_test)   
            
                        get_open_order = client_b.futures_position_information(symbol = COIN)
                        value = float(get_open_order[0]['notional'])

                        if df['SEÑAL'][Last_signal_1] == 1 and value == 0:

                            #print('orden de compra generada')

                            account_info = client_b.futures_account_balance()

                            for info in range(0, len(account_info), 1):
                
                                if account_info[info]['asset'] == 'USDT':

                                    limite = float(account_info[info]['withdrawAvailable'])
                            
                            if limite > cantidad_limite:

                                #print('supera limite')
                                #print(COIN)

                                history = client_b.futures_income_history(symbol = COIN)

                                if len(history) != 0:

                                    last_trade = datetime.fromtimestamp(float(history[-1]['time'])/1000)
                
                                else:

                                    last_trade = df['timestamp'][len(df)-50] 

                                ultimate_date = df['timestamp'][Last_signal_1]

                                if last_trade < ultimate_date:
                                    #print('es el primer trade de esta moneda')

                                    get_open_order = client_b.futures_position_information(symbol = COIN)
                                    value = float(get_open_order[0]['notional'])
                                    
                                    if df['Signal'][Last_signal_1] == 'BUY' and df['rsi_14'][Last_signal_1] < 67 and df['ERI'][Last_signal_1] == 'BUY' and df['Trend'][Last_signal_1] == 'BUY' and value == 0:
                                    
                                        value_coin = float(client_b.futures_symbol_ticker(symbol= COIN)['price'])
                                        cantidad_coin = round(cantidad_usd/value_coin,0)

                                        create_order = client_b.futures_create_order(symbol= COIN,side='BUY',type="MARKET",
                                                                                    quantity=cantidad_coin)
                                
                                        date_today = datetime.today()
                                        timestamp_today = datetime.timestamp(date_today)

                                        print('se creo orden de compra, '+str(datetime.today()))
                                        fecha_test_1 = df['timestamp'][Last_signal_1]
                                        print(fecha_test_1)    
                                        print(COIN)        
                                
                                    if df['Signal'][Last_signal_1] == 'SELL' and df['rsi_14'][Last_signal_1] > 33 and df['ERI'][Last_signal_1] == 'SELL' and df['Trend'][Last_signal_1] == 'SELL' and value == 0:

                                        value_coin = float(client_b.futures_symbol_ticker(symbol= COIN)['price'])
                                        cantidad_coin = round(cantidad_usd/value_coin,0)

                                        create_order = client_b.futures_create_order(symbol= COIN,side='SELL',type="MARKET",
                                                                                    quantity=cantidad_coin)
                                
                                        date_today = datetime.today()
                                        timestamp_today = datetime.timestamp(date_today)

                                        print('se creo orden de venta, '+str(datetime.today()))
                                        fecha_test_1 = df['timestamp'][Last_signal_1]
                                        print(fecha_test_1)
                                        print(COIN)
            
    except ccxt.BaseError as Error:
        print ("[ERROR] ", Error )
        continue                   
     
        