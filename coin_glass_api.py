import json
import time
import datetime
import requests
from binance_api import BinanceAPI
import progressbar
import config

total_iterations = 100
bar = progressbar.ProgressBar(maxval=total_iterations,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

class CoinglassAPI():
    def __init__(self) -> None:
        self.headers = {
            "accept": "application/json",
            "coinglassSecret": "7160da0a0363452eb37f029dada93013"
        }
    
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
        try:
            response = requests.get(url, headers=self.headers)
        except:
            print("Could not get response from ", symbol)
            return None
        # print(response.text)
        return json.loads(response.text)

class DetermineTOPN():
    def __init__(self, futures_or_not):
        self.futures_or_not = futures_or_not
        self.last_top_N_usdt_pair_names = None
        self.last_top_250_usdt_pair_names = None

    def compare_with_last_time(self, top_N_usdt_pair_names, top_250_usdt_pair_names):
        # 跟上次的結果比較多了哪些新幣
        if self.last_top_N_usdt_pair_names == None:
            self.last_top_N_usdt_pair_names = top_N_usdt_pair_names
            self.last_top_250_usdt_pair_names = top_250_usdt_pair_names
        else:
            # 比較舊的跟新的多了那些 pair
            for i in range(len(top_N_usdt_pair_names)):
                pair = top_N_usdt_pair_names[i]
                if pair not in self.last_top_N_usdt_pair_names:
                    try:
                        last_index = self.last_top_250_usdt_pair_names.index(pair)
                        print("這次新增: ", pair, " 是第 ", i, " 名")
                        print(pair, "在上一輪是第", last_index, "名")
                    except:
                        last_index = 999
                        print("上次不在前 250 名裡，這次是第 ", i, " 名")
                    
                    # 如果上升三名才回報
                    if last_index - i >= 3:
                        telegram_bot_sendtext("這次新增: " + pair + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名")
            print("\n")
            self.last_top_N_usdt_pair_names = top_N_usdt_pair_names
            self.last_top_250_usdt_pair_names = top_250_usdt_pair_names

    def compare(self, top_250_usdt_pair_names):
        if self.last_top_250_usdt_pair_names == None:
            self.last_top_250_usdt_pair_names = top_250_usdt_pair_names
        else:
            for i in range(len(top_250_usdt_pair_names)):
                if top_250_usdt_pair_names[i] in self.last_top_250_usdt_pair_names:
                    # 比較上升了幾名
                    last_index = self.last_top_250_usdt_pair_names.index(top_250_usdt_pair_names[i])
                    if last_index - i >= 3:
                        if self.futures_or_not:
                            telegram_bot_sendtext("合約部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")
                            print("合約部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")
                        else:
                            telegram_bot_sendtext("現貨部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")
                            print("現貨部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")

                else:
                    # 表示是新進榜的
                    last_index = 999
                    if self.futures_or_not:
                        telegram_bot_sendtext("合約部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")
                        print("合約部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")
                    else:
                        telegram_bot_sendtext("現貨部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")
                        print("現貨部分，這次新增: " + top_250_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名")

            self.last_top_250_usdt_pair_names = top_250_usdt_pair_names

def telegram_bot_sendtext(bot_message):
    bot_token = config.TELEGRAM_API
    MY_TELEGRAM_ID = config.MY_TELEGRAM_ID

    # 送訊息給我
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + MY_TELEGRAM_ID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

    return response.json()

class FundingRate():
    def __init__(self):
        self.strange_funding_rate_list = []

    def analyze_funding_rate_and_report(self, top_100_usdt_pair_informations):
        for key in top_100_usdt_pair_informations.keys():
            funding_rate = top_100_usdt_pair_informations[key]["fundingRate"]
            
            # 如果有資金費率異常的幣種
            if funding_rate <= -1.5 or funding_rate >= 1:
                # 如果不在觀察清單裡
                if key not in self.strange_funding_rate_list:
                    # 回報資金費率異常的幣種
                    print("strange funding rate: " + key + " / " + str(funding_rate))
                    telegram_bot_sendtext("strange funding rate: " + key + " / " + str(funding_rate))
                    self.strange_funding_rate_list.append(key)
            else:    
                # 檢察觀察清單裡的幣種，資金費率是不是回到正常水平
                if key in self.strange_funding_rate_list:
                    print("funding rate become normal: " + key + " / " + str(funding_rate))
                    telegram_bot_sendtext("funding rate become normal: " + key + " / " + str(funding_rate))
                    self.strange_funding_rate_list.remove(key)


if __name__ == "__main__":
    coinglass_api = CoinglassAPI()
    binance_api = BinanceAPI()

    determine_top_250 = DetermineTOPN(False)
    determine_top_250_futures = DetermineTOPN(True)

    funding_rate = FundingRate()
    
    # 主要的 while 迴圈
    while True:
        current_time = time.localtime()
        
        if current_time.tm_min % 5 == 0:
            print("------------------------check top 250  ------------------------")
            result = binance_api.get_top_250_pairs()
            if result is not None:
                _, top_250_usdt_pair_names, _, _ = result
                determine_top_250.compare(top_250_usdt_pair_names)


            print("------------------------check top 250 futures ------------------------")
            result = binance_api.get_top_250_futures_pairs()
            if result is not None:
                _, top_250_futures_usdt_pair_names, _, _ = result
                determine_top_250_futures.compare(top_250_futures_usdt_pair_names)

        # 檢查分鐘是否是 15 的倍數，15 分鐘更新一次
        if current_time.tm_min % 15 == 0:
            # 拿幣安合約成交量前 250 名的資料
            top_250_usdt_pairs, top_250_usdt_pair_names, top_250_usdt_pair_volume, top_250_usdt_pair_pricechangepercent = binance_api.get_top_250_futures_pairs()
            
            top_100_usdt_pair_names = top_250_usdt_pair_names[:100]
            # top_100_usdt_pair_volume = top_250_usdt_pair_volume[:100]
            # top_100_usdt_pair_pricechangepercent = top_250_usdt_pair_pricechangepercent[:100]

            # 拿這些幣的合約資料
            top_100_usdt_pair_informations = {} 
            print("get top 100 usdt pairs...")
            bar.start()
            for i in range(len(top_100_usdt_pair_names)):
                pair = top_100_usdt_pair_names[i]
                # volume = top_100_usdt_pair_volume[i]
                # pricechangepercent = top_100_usdt_pair_pricechangepercent[i]

                main_coin = pair.replace("USDT", "")
                base_coin = "USDT"
                
                # get perpetual market informations
                perpetual_market = coinglass_api.get_perpetual_market(main_coin)
                time.sleep(2)
                # print(perpetual_market['data'][main_coin][0])
                try: 
                    coin_informations = perpetual_market['data'][main_coin][0]
                    top_100_usdt_pair_informations[pair] = coin_informations
                except:
                    pass
                    # print("this coin don't have perpetual market.")

                bar.update(i + 1)
            bar.finish()

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
                json.dump(top_250_usdt_pairs, json_file, indent=4)

            # 檢查資金費率
            funding_rate.analyze_funding_rate_and_report(top_100_usdt_pair_informations)

        # 等待 30 秒，避免無限迴圈過於頻繁
        time.sleep(30)