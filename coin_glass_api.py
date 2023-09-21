import json
import time
import requests
from binance_api import BinanceAPI

class CoinglassAPI():
    def __init__(self) -> None:
        self.headers = {
            "accept": "application/json",
            "coinglassSecret": "7160da0a0363452eb37f029dada93013"
        }

    def get_instrument(self) -> dict:
        """ response data structure
        {
            "code": "0",
            "msg": "success",
            "data": {
                "Binance": [
                {
                    "instrumentId": "BTCUSD_PERP",
                    "baseAsset": "BTC",
                    "quoteAsset": "USD"
                },
                {
                    "instrumentId": "BTCUSD_230929",
                    "baseAsset": "BTC",
                    "quoteAsset": "USD"
                },......]
            },
                "Bingx": [....],
            "success": "True"
        }
        """
        instrument_url = "https://open-api.coinglass.com/public/v2/instrument"
        response = requests.get(instrument_url, headers=self.headers)
        return json.loads(response.text)
    
    def get_perpetual_market(self, symbol) -> dict:
        """
        {
        "code": "0",
        "msg": "success",
        "data": {
            "BTC": [
            {
                "exchangeName": "Binance",
                "originalSymbol": "BTCUSDT",
                "symbol": "BTC",
                "price": 27142.7,
                "type": 1,
                "updateTime": 1695127862301,
                "quoteCurrency": "USDT",
                "turnoverNumber": 4048733,
                "longRate": 49.48,
                "longVolUsd": 5635174565.3856,
                "shortRate": 50.52,
                "shortVolUsd": 5752789615.4764,
                "exchangeLogo": "https://cdn.coinglasscdn.com/static/exchanges/270.png",
                "symbolLogo": "https://cdn.coinglasscdn.com/static/img/coins/bitcoin-BTC.png",
                "totalVolUsd": 11387964180.862,
                "rate": 27.52,
                "highPrice": 27470,
                "lowPrice": 26611.2,
                "openInterestAmount": 93584.746,
                "openInterest": 2539768346.2702,
                "openPrice": 27346.6,
                "priceChange": -203.9,
                "priceChangePercent": -0.75,
                "indexPrice": 27149.91582418,
                "buyTurnoverNumber": 2011277,
                "sellTurnoverNumber": 2037456,
                "fundingRate": -0.002005,
                "nextFundingTime": 1695139200000
            },...]
        },
        "success": "True"
        }
        """
        url = "https://open-api.coinglass.com/public/v2/perpetual_market?symbol=" + symbol
        response = requests.get(url, headers=self.headers)
        # print(response.text)
        return json.loads(response.text)

if __name__ == "__main__":
    coinglass_api = CoinglassAPI()
    binance_api = BinanceAPI()
    
    last_top_100_usdt_pair_names = None

    # 主要的 while 迴圈
    while True:
        current_time = time.localtime()
        
        # 檢查分鐘是否是五的倍數
        if current_time.tm_min % 5 == 0:
            top_100_usdt_pairs, top_100_usdt_pair_names, top_100_usdt_pair_volume = binance_api.get_top_100_pairs()
            for i in range(len(top_100_usdt_pair_names)):
                pair = top_100_usdt_pair_names[i]
                volume = top_100_usdt_pair_volume[i]
                # print(pair)
                main_coin = pair.replace("USDT", "")
                base_coin = "USDT"
                
                # get market informations
                perpetual_market = coinglass_api.get_perpetual_market(main_coin)
                time.sleep(2)
                # print(perpetual_market['data'][main_coin][0])
                try: 
                    coin_informations = perpetual_market['data'][main_coin][0]
                    price = coin_informations['price']
                    funding_rate = coin_informations['fundingRate']
                    open_interest = coin_informations['openInterestAmount']
                    # print(price, funding_rate, open_interest, volume)
                except:
                    pass
                    # print("this coin don't have perpetual market.")

            if last_top_100_usdt_pair_names == None:
                last_top_100_usdt_pair_names = top_100_usdt_pair_names
            else:
                # 比較舊的跟新的多了那些 pair
                import datetime

                # 獲取當前時間
                current_time = datetime.datetime.now()

                # 提取年、月、日、小時和分鐘
                year = current_time.year
                month = current_time.month
                day = current_time.day
                hour = current_time.hour
                minute = current_time.minute

                # 印出年、月、日、小時和分鐘在同一行
                print("更新!!!")
                print(f"年：{year}, 月：{month}, 日：{day}, 小時：{hour}, 分鐘：{minute}")

                for i in range(len(top_100_usdt_pair_names)):
                    pair = top_100_usdt_pair_names[i]
                    if pair not in last_top_100_usdt_pair_names:
                        print("這次新增: ", pair, " 是第 ", i, " 名")

                print("\n")
                last_top_100_usdt_pair_names = top_100_usdt_pair_names

        # 等待一分鐘，避免無限迴圈過於頻繁
        time.sleep(60)