import requests
import json
import config
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

class BinanceAPI:
    def __init__(self):
        # 你的Binance API密鑰
        self.api_key = config.API_KEY
        self.api_secret = config.API_PRIVATE_KEY
        # Binance API的基本URL
        self.base_url = 'https://api.binance.com/api/v3'
        self.future_url = 'https://fapi.binance.com/fapi/v1'

    def get_top_300_pairs(self):
        # 請求的端點
        endpoint = '/ticker/24hr'
        # 發送HTTP GET請求
        try:
            response = session.get(f'{self.base_url}{endpoint}')
        except:
            return None
        # 解析JSON回應
        data = response.json()
        # 過濾出以USDT為基底的交易對
        usdt_pairs = [pair for pair in data if pair['symbol'].endswith('USDT')]
        # 要排除的穩定幣交易對列表
        exclude_pairs = ['USDCUSDT', 'FDUSDUSDT', 'BUSDUSDT', 'TUSDUSDT', 'USDPUSDT', 'USTCUSDT']
        # 排除指定的穩定幣交易對
        filtered_usdt_pairs = [pair for pair in usdt_pairs if pair['symbol'] not in exclude_pairs]
        # 根據交易金額（quoteVolume）對交易對進行排序
        filtered_usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
        # print(len(filtered_usdt_pairs)) 460

        # 選擇前300大交易金額的交易對
        top_300_usdt_pairs = filtered_usdt_pairs[:300]
        # 提取交易對的名稱
        top_300_usdt_pair_names = [pair['symbol'] for pair in top_300_usdt_pairs]
        # 提取交易對的成交量
        top_300_usdt_pair_volume = [pair['quoteVolume'] for pair in top_300_usdt_pairs]
        # 提取交易對的價格變化百分比
        top_300_usdt_pair_pricechangepercent = [pair['priceChangePercent'] for pair in top_300_usdt_pairs]
        # 列印前10大交易金額的交易對
        # print('前100大以USDT為基底的交易對:')
        # for pair in top_100_usdt_pair_names:
        #     print(pair)
        
        return top_300_usdt_pairs, top_300_usdt_pair_names, top_300_usdt_pair_volume, top_300_usdt_pair_pricechangepercent
    
    def get_top_300_futures_pairs(self):
        # 請求的端點
        endpoint = '/ticker/24hr'
        # 發送HTTP GET請求
        # print(f'{self.future_url}{endpoint}')
        response = session.get(f'{self.future_url}{endpoint}')
        # print(response)
        # 解析JSON回應
        data = response.json()
        # 過濾出以USDT為基底的交易對
        usdt_pairs = [pair for pair in data if pair['symbol'].endswith('USDT')]
        # 要排除的穩定幣交易對列表
        exclude_pairs = ['USDCUSDT', 'FDUSDUSDT', 'BUSDUSDT', 'TUSDUSDT']
        # 排除指定的穩定幣交易對
        filtered_usdt_pairs = [pair for pair in usdt_pairs if pair['symbol'] not in exclude_pairs]
        # 根據交易金額（quoteVolume）對交易對進行排序
        filtered_usdt_pairs.sort(key=lambda x: float(x['quoteVolume']), reverse=True)
        # 選擇前300大交易金額的交易對
        top_300_usdt_pairs = filtered_usdt_pairs[:300]
        # 提取交易對的名稱
        top_300_usdt_pair_names = [pair['symbol'] for pair in top_300_usdt_pairs]
        # 提取交易對的成交量
        top_300_usdt_pair_volume = [pair['quoteVolume'] for pair in top_300_usdt_pairs]
        # 提取交易對的價格變化百分比
        top_300_usdt_pair_pricechangepercent = [pair['priceChangePercent'] for pair in top_300_usdt_pairs]

        return top_300_usdt_pairs, top_300_usdt_pair_names, top_300_usdt_pair_volume, top_300_usdt_pair_pricechangepercent
    
    def get_volume_information(self, symbol):
        ''' 獲取某段時間區間內的 K 棒資料
            symbol 交易對 BTCUSDT
            interval 時間區間
            start_time 開始時間
            end_time 結束時間
            limit 回傳上限 default 500 max 1000
        '''
        '''  回傳內容
        [
            [
                // Kline open time
                // Open price
                // High price
                // Low price
                // Close price
                // Volume
                // Kline Close time
                // Quote asset volume
                // Number of trades
                // Taker buy base asset volume
                // Taker buy quote asset volume
                // Unused field, ignore.
            ]
        ]
        '''
        # print("processing", symbol)

        interval = '5m'  # 時間間隔，比如1小時
        start_time = int((time.time() - 87000) * 1000)  # 開始時間，格式需符合ISO 8601，time.time() 是以秒為單位，乘1000轉毫秒
        end_time = int((time.time() -300) * 1000) # 五分鐘 = 300 秒 

        # 組建 API 請求
        url = f'https://api.binance.com/api/v3/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time
        }
        headers = {'X-MBX-APIKEY': self.api_key}
        response = session.get(url, params=params, headers=headers)

        klines = []
        now_volume = 0
        avg_volume = 0
        # 處理 API 回應
        if response.status_code == 200:
            klines = response.json()
        else:
            print(f'錯誤：{response.status_code}, {response.text}')

        if len(klines) == 289:
            total_volume = 0
            for i in range(len(klines)):
                if i != len(klines) - 1:
                    total_volume += float(klines[i][7])

            avg_volume = total_volume / (len(klines) - 1)
            now_volume = float(klines[-1][7])
            # print(avg_volume, now_volume)

        return now_volume, avg_volume, klines

    def get_future_volume_information(self, symbol):
        ''' 獲取某段時間區間內的 K 棒資料
            symbol 交易對 BTCUSDT
            interval 時間區間
            start_time 開始時間
            end_time 結束時間
            limit 回傳上限 default 500 max 1000
        '''
        # print("processing", symbol)

        interval = '5m'  # 時間間隔，比如1小時
        start_time = int((time.time() - 87000) * 1000)  # 開始時間，格式需符合ISO 8601，time.time() 是以秒為單位，乘1000轉毫秒
        end_time = int((time.time() -300) * 1000) # 五分鐘 = 300 秒 

        # 組建 API 請求
        url = f'https://fapi.binance.com/fapi/v1/klines'
        params = {
            'symbol': symbol,
            'interval': interval,
            'startTime': start_time,
            'endTime': end_time
        }
        headers = {'X-MBX-APIKEY': self.api_key}
        response = requests.get(url, params=params, headers=headers)

        klines = []
        now_volume = 0
        avg_volume = 0
        # 處理 API 回應
        if response.status_code == 200:
            klines = response.json()
            # print(len(klines))
            # print(klines[-1])
        else:
            print(f'錯誤：{response.status_code}, {response.text}')

        if len(klines) == 289:
            total_volume = 0
            for i in range(len(klines)):
                if i != len(klines) - 1:
                    total_volume += float(klines[i][7])

            avg_volume = total_volume / (len(klines) - 1)
            now_volume = float(klines[-1][7])
            # print(avg_volume, now_volume)
        
        return now_volume, avg_volume, klines
    
if __name__ == '__main__':
    api = BinanceAPI()
    top_300_usdt_pairs, top_300_usdt_pair_names, top_300_usdt_pair_volume, top_300_usdt_pair_pricechangepercent = api.get_top_300_pairs()
    top_300_usdt_pairs, top_300_usdt_pair_names, top_300_usdt_pair_volume, top_300_usdt_pair_pricechangepercent = api.get_top_300_futures_pairs()
    print(top_300_usdt_pairs[0])
    for top_300_usdt_name in top_300_usdt_pair_names[:1]:
        now_volume, avg_volume, klines = api.get_future_volume_information(top_300_usdt_name)
        print(klines[-1])
        time.sleep(0.1)
