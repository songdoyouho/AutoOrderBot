import json
import time
import datetime
import requests
from binance_api import BinanceAPI
import progressbar

total_iterations = 100
bar = progressbar.ProgressBar(maxval=total_iterations,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

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

class DetermineTOPN():
    def __init__(self):
        self.last_top_N_usdt_pair_names = None
        self.last_top_200_usdt_pair_names = None

    def compare_with_last_time(self, top_N_usdt_pair_names, top_200_usdt_pair_names):
        # 跟上次的結果比較多了哪些新幣
        if self.last_top_N_usdt_pair_names == None:
            self.last_top_N_usdt_pair_names = top_N_usdt_pair_names
            self.last_top_200_usdt_pair_names = top_200_usdt_pair_names
        else:
            # 比較舊的跟新的多了那些 pair
            for i in range(len(top_N_usdt_pair_names)):
                pair = top_N_usdt_pair_names[i]
                if pair not in self.last_top_N_usdt_pair_names:
                    print("這次新增: ", pair, " 是第 ", i, " 名")
                    last_index = self.last_top_200_usdt_pair_names.index(pair)
                    print(pair, "在上一輪是第", last_index, "名")
            print("\n")
            self.last_top_N_usdt_pair_names = top_N_usdt_pair_names
            self.last_top_200_usdt_pair_names = top_200_usdt_pair_names


if __name__ == "__main__":
    coinglass_api = CoinglassAPI()
    binance_api = BinanceAPI()
    determine_top_100 = DetermineTOPN()
    determine_top_50 = DetermineTOPN()
    determine_top_25 = DetermineTOPN()
    determine_top_10 = DetermineTOPN()
    
    # 主要的 while 迴圈
    while True:
        current_time = time.localtime()
        
        # 檢查分鐘是否是五的倍數
        if current_time.tm_min % 15 == 0:
            # 拿幣安現貨成交量前N名的資料
            top_200_usdt_pairs, top_200_usdt_pair_names, top_200_usdt_pair_volume, top_200_usdt_pair_pricechangepercent = binance_api.get_top_200_futures_pairs()
            
            top_100_usdt_pairs = top_200_usdt_pairs[:100]
            top_100_usdt_pair_names = top_200_usdt_pair_names[:100]
            top_100_usdt_pair_volume = top_200_usdt_pair_volume[:100]
            top_100_usdt_pair_pricechangepercent = top_200_usdt_pair_pricechangepercent[:100]

            # 拿這些幣的合約資料
            top_100_usdt_pair_informations = {}
            print("get top 100 usdt pairs...")
            bar.start()
            for i in range(len(top_100_usdt_pair_names)):
                pair = top_100_usdt_pair_names[i]
                volume = top_100_usdt_pair_volume[i]
                pricechangepercent = top_100_usdt_pair_pricechangepercent[i]

                main_coin = pair.replace("USDT", "")
                base_coin = "USDT"
                
                # get market informations
                perpetual_market = coinglass_api.get_perpetual_market(main_coin)
                time.sleep(2)
                # print(perpetual_market['data'][main_coin][0])
                try: 
                    coin_informations = perpetual_market['data'][main_coin][0]
                    top_100_usdt_pair_informations[pair] = coin_informations
                    # price = coin_informations['price']
                    # funding_rate = coin_informations['fundingRate']
                    # open_interest = coin_informations['openInterestAmount']
                    # print(price, funding_rate, open_interest, volume)

                    # top_100_usdt_pair_informations[pair] = {
                    #     'volume': volume,
                    #     'price': price,
                    #     'funding_rate': funding_rate,
                    #     'open_interest': open_interest,
                    #     'pricechangepercent': pricechangepercent,
                    # }
                except:
                    # top_100_usdt_pair_informations[pair] = {
                    #     'volume': None,
                    #     'price': None,
                    #     'funding_rate': None,
                    #     'open_interest': None,
                    #     'pricechangepercent': None,
                    # }
                    pass
                    # print("this coin don't have perpetual market.")

                bar.update(i + 1)
            bar.finish()

            top_50_usdt_pair_names = top_100_usdt_pair_names[:50]
            top_25_usdt_pair_names = top_100_usdt_pair_names[:25]
            top_10_usdt_pair_names = top_100_usdt_pair_names[:10]
            # 獲取當前時間
            current_time = datetime.datetime.now()
            # 提取年、月、日、小時和分鐘
            year = current_time.year
            month = current_time.month
            day = current_time.day
            hour = current_time.hour
            minute = current_time.minute
            # 印出年、月、日、小時和分鐘在同一行
            print(f"{year}年 {month}月 {day}日 {hour}：{minute}")
            
            # 輸出得到的資料
            perp_json_filename = "data/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_perpetual.json'
            with open(perp_json_filename, "w") as json_file:
                json.dump(top_100_usdt_pair_informations, json_file, indent=4)

            binance_json_filename = "data/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_binance.json'
            with open(binance_json_filename, "w") as json_file:
                json.dump(top_200_usdt_pairs, json_file, indent=4)

            print("前 100 名 -> ")
            determine_top_100.compare_with_last_time(top_100_usdt_pair_names, top_200_usdt_pair_names)
            print("前 50 名 -> ")
            determine_top_50.compare_with_last_time(top_50_usdt_pair_names, top_200_usdt_pair_names)
            print("前 25 名 -> ")
            determine_top_25.compare_with_last_time(top_25_usdt_pair_names, top_200_usdt_pair_names)
            print("前 10 名 -> ")
            determine_top_10.compare_with_last_time(top_10_usdt_pair_names, top_200_usdt_pair_names)

        # 等待一分鐘，避免無限迴圈過於頻繁
        time.sleep(30)