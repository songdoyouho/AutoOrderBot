import requests
import json
import config

class BinanceAPI:
    def __init__(self):
        # 你的Binance API密鑰
        self.api_key = config.API_KEY
        self.api_secret = config.API_PRIVATE_KEY
        # Binance API的基本URL
        self.base_url = 'https://api.binance.com/api/v3'

    def get_top_100_pairs(self):
        # 請求的端點
        endpoint = '/ticker/24hr'
        # 發送HTTP GET請求
        response = requests.get(f'{self.base_url}{endpoint}')
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
        # 選擇前100大交易金額的交易對
        top_100_usdt_pairs = filtered_usdt_pairs[:100]
        # 提取交易對的名稱
        top_100_usdt_pair_names = [pair['symbol'] for pair in top_100_usdt_pairs]
        # 提取交易對的成交量
        top_100_usdt_pair_volume = [pair['quoteVolume'] for pair in top_100_usdt_pairs]

        # 列印前10大交易金額的交易對
        # print('前100大以USDT為基底的交易對:')
        # for pair in top_100_usdt_pair_names:
        #     print(pair)
        
        return top_100_usdt_pairs, top_100_usdt_pair_names, top_100_usdt_pair_volume
    
if __name__ == '__main__':
    api = BinanceAPI()
    top_100_usdt_pairs, top_100_usdt_pair_names, top_100_usdt_pair_volume = api.get_top_100_pairs()
