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

url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/info'
parameters = {
    'CMC_PRO_API_KEY': config.CMC_API_KEY,
    'symbol': 'LPT',  # 例如：'BTC'
}

headers = {
    'Accepts': 'application/json',
}

response = session.get(url, headers=headers, params=parameters)

if response.status_code == 200:
    data = response.json()
    # 在這裡處理返回的JSON數據，例如提取市值、流通供應量、總供應量等信息
    coin_info = data['data']['LPT']  # 例如：'BTC'

    print(coin_info)
    # current supply 跟 24 小時交易量在 'description' 裡，但是要分離出來

else:
    print(f"錯誤代碼：{response.status_code}")
    print(response.text)