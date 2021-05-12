import asyncio
import json
import time
from colorama import init, Fore
from binance import AsyncClient, DepthCacheManager, BinanceSocketManager
import threading


pair = "SHIBUSDT" # Current Pair, it's not tested with small coins with decimals.
debug = False # Prints everything that can be printed.
interval_trade = 1 # Interval to check trading history, set at 1 for very high volume pairs.
trade_trend = [] # Trend Array, here we save the totalsell and the totalbuy
trade_trend_interval = 14 # How many updates required to get the current trending.
api_key = ""
api_secret = ""

init()
# print("Bienvenido a Jonirulah Tracker v0.1")
print("El intervalo de actualizaciones para " + Fore.RED + "get_recent_trades " + Fore.RESET + "está en " + Fore.YELLOW + str(interval_trade) + Fore.CYAN +"s" + Fore.RESET)
print("El programa empezará en 2 segundos.\n")
time.sleep(2)

def Formatter(qty):
    try:
        qty = int(qty)
        qty = str(qty)
        if len(qty) == 1:
            cantidad = str(qty[0] + "u")   
        elif len(qty) == 2:
            cantidad = str(qty[0:2] + "u")   
        elif len(qty) == 3:
            cantidad = str(qty[0:3] + "u")   
        elif len(qty) == 4:
            cantidad = str(qty[0] + "k")   
        elif len(qty) == 5:
            cantidad = str(qty[0:2] + "k")   
        elif len(qty) == 6:
            cantidad = str(qty[0:3] + "k") 
        elif len(qty) == 7:
            cantidad = str(qty[0] + "M")   
        elif len(qty) == 8:
            cantidad = str(qty[0:2] + "M")
        elif len(qty) == 9:
            cantidad = str(qty[0:3] + "M") 
        elif len(qty) == 10:
            cantidad = str(qty[0:4] + "M")   
        elif len(qty) == 11:
            cantidad = str(qty[0:5] + "M")
        elif len(qty) == 12:
            cantidad = str(qty[0:6] + "M") 
        elif len(qty) == 13:
            cantidad = str(qty[0] + "B")   
        elif len(qty) == 14:
            cantidad = str(qty[0:1] + "B")
        elif len(qty) == 15:
            cantidad = str(qty[0:2] + "B") 
        return str(cantidad)
    except:
        return str(-1)


def GetDate():
	x = datetime.datetime.utcnow()
	x = x.strftime("%d/%m/%Y %H:%M:%S")
	x = "[" + x + " UTC] "
	return x

def TrendCheck():
    global trade_trend, trade_trend_interval, debug
    time.sleep(3)
    while True:
        total_trade_volume = 0
        for x in trade_trend:
            total_trade_volume = total_trade_volume + int(x)
        if total_trade_volume > 0:
            status_trend = Fore.RESET + "[" + Fore.GREEN + "POSITIVA" + Fore.RESET + "]"
            raw_status = "positive"
        else:
            status_trend = Fore.RESET + "[" + Fore.RED + "NEGATIVA" + Fore.RESET + "]"
            raw_status = "negative"
        print(Fore.RESET + "[" + Fore.YELLOW +  pair + Fore.RESET + "] " + Fore.CYAN + "La tendencia es " + Formatter(str(total_trade_volume)) + " " + status_trend)
        time.sleep(5)

async def main():
    global pair, debug, interval_trade, trade_trend, trade_trend_interval, api_key, api_secret
    client = await AsyncClient.create(api_key, api_secret)
    ExecTrendCheck = threading.Thread(target=TrendCheck)
    ExecTrendCheck.setDaemon(False)
    ExecTrendCheck.start()
    maxid = 0
    while True:
        totalbuy = 0.0
        totalsell = 0.0
        tickers = await client.get_recent_trades(symbol=pair)
        # print("[" + Fore.YELLOW + pair + Fore.RESET + "] Checking recent trades...")
        for x in tickers:
            if x["id"] > maxid:
                maxid = x["id"]       
                format2 = Formatter(float(x["qty"])) 
                # Sell order
                if x["isBuyerMaker"] == True:
                    if debug:
                        print(Fore.RESET + "[" + Fore.RED + "BIG SELL" + Fore.RESET + "] " + Fore.GREEN + "ID " + str(x['id']) + " | Precio: " + x['price'] + " | Cantidad: " + format2)
                    if "M" in format2:
                        format = format2.replace("M","")
                        if int(format) > 150:
                            price = round(float(x["qty"]) * float(x["price"]), 2)
                            print(Fore.RESET + "[" + Fore.RED + "BIG SELL" + Fore.RESET + "] " + Fore.GREEN + "ID " + str(x['id']) + " | Precio: " + x['price'] + " | Cantidad: " + format2 + " | Total: " + str(price) + "$")

                    totalsell = totalsell + float(x["qty"])
                # Buy Order
                elif x["isBuyerMaker"] == False:
                    if debug:
                        print(Fore.RESET + "[" + Fore.GREEN + "BIG BUY" + Fore.RESET + "] " + Fore.RED + "ID " + str(x['id']) + " | Precio: " + x['price'] + " | Cantidad: " + format2)
                    if "M" in format2:
                        format = format2.replace("M","")
                        if int(format) > 150:
                            price = round(float(x["qty"]) * float(x["price"]), 2)
                            print(Fore.RESET + "[" + Fore.GREEN + "BIG BUY" + Fore.RESET + "] " + Fore.RED + "ID " + str(x['id']) + " | Precio: " + x['price'] + " | Cantidad: " + format2 + " | Total: " + str(price) + "$")
                    totalbuy = totalbuy + float(x["qty"])
        total_now = totalbuy - totalsell

        if len(trade_trend) >= 10:
            trade_trend.pop(0)
             
        trade_trend.append(total_now)

        print(Fore.RESET + "[" + Fore.YELLOW + pair + Fore.RESET +"] " + Fore.RESET + "Total SELL: " + Fore.RED + Formatter(totalsell) + Fore.RESET +  " | Total BUY: " + Fore.GREEN + Formatter(totalbuy) + Fore.RESET)
        time.sleep(interval_trade)


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())