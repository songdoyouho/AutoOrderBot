import json
import time
import datetime
import requests
from binance_api import BinanceAPI
import progressbar
import config
from coin_glass_api import CoinglassAPI
from utils import *

total_iterations = 100
bar_for_coinglass = progressbar.ProgressBar(maxval=total_iterations,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

total_iterations = 300
bar_for_volume = progressbar.ProgressBar(maxval=total_iterations,
                              widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])

if __name__ == "__main__":
    coinglass_api = CoinglassAPI()
    binance_api = BinanceAPI()

    determine_top_300 = DetermineTOPN(False)
    determine_top_300_futures = DetermineTOPN(True)

    funding_rate = FundingRate()
    
    # 主要的 while 迴圈
    while True:
        current_time = time.localtime()

        # 獲取當前時間
        now_time = datetime.datetime.now()
        # 提取年、月、日、小時和分鐘
        year = now_time.year
        month = now_time.month
        day = now_time.day
        hour = now_time.hour
        minute = now_time.minute
        
        if current_time.tm_min % 5 == 0: # 每五分鐘
            result = binance_api.get_top_300_pairs()
            if result is not None:
                top_300_usdt_pairs, top_300_usdt_pair_names, top_300_usdt_pair_volume, top_300_usdt_pair_pricechangepercent = result
                # determine_top_300.compare(top_300_usdt_pair_names, top_300_usdt_pair_pricechangepercent)

                klines_list = []
                print("------------------------check top 300 spots ------------------------")
                print("")
                bar_for_volume.start()
                for j in range(len(top_300_usdt_pair_names)):
                    top_300_usdt_name = top_300_usdt_pair_names[j]
                    now_volume, avg_volume, klines = binance_api.get_volume_information(top_300_usdt_name)
                    klines_list.append([top_300_usdt_name, klines])
                    if now_volume > avg_volume * 10 and float(klines[-1][10]) > 1000000: # 檢查現貨成交量是否異常
                        telegram_bot_sendtext("現貨成交量大爆射: " + top_300_usdt_name + "主動買量:" + str(klines[-1][10]))

                    if now_volume > avg_volume * 10: # 如果有大量成交量，記錄下來
                        # 先讀之前的資料
                        json_file_path = 'spot_volume_history.json'
                        with open(json_file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                        # 新增這次的資訊
                        if top_300_usdt_name in data:
                            data[top_300_usdt_name].append([str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute), klines[-1]])
                        else:
                            data[top_300_usdt_name] = [[str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute), klines[-1]]]

                        with open(json_file_path, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=4)

                    time.sleep(0.1)
                    bar_for_volume.update(j + 1)
                bar_for_volume.finish()

                # save klines_list
                klines_list_filename = "klines/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_spot.json'
                with open(klines_list_filename, "w") as json_file:
                    json.dump(klines_list, json_file, indent=4)

            
            result = binance_api.get_top_300_futures_pairs()
            if result is not None:
                top_300_futures_usdt_pairs, top_300_futures_usdt_pair_names, top_300_futures_usdt_pair_volume, top_300_futures_usdt_pair_pricechangepercent = result
                # determine_top_300_futures.compare(top_300_futures_usdt_pair_names, top_300_futures_usdt_pair_pricechangepercent)

                klines_list = []
                print("------------------------check top 300 perpetuals ------------------------")
                bar_for_volume.start()
                for j in range(len(top_300_futures_usdt_pair_names)):
                    top_300_futures_usdt_name = top_300_futures_usdt_pair_names[j]
                    now_volume, avg_volume, klines = binance_api.get_future_volume_information(top_300_futures_usdt_name)
                    klines_list.append([top_300_futures_usdt_name, klines])
                    if now_volume > avg_volume * 10 and float(klines[-1][10]) > 1000000:
                        telegram_bot_sendtext("合約成交量大爆射: " + top_300_futures_usdt_name + " 主動買量:" + str(klines[-1][10]))

                    if now_volume > avg_volume * 10:
                        # 先讀之前的資料
                        json_file_path = 'perpetual_volume_history.json'
                        with open(json_file_path, 'r', encoding='utf-8') as file:
                            data = json.load(file)

                        # 新增這次的資訊
                        if top_300_futures_usdt_name in data:
                            data[top_300_futures_usdt_name].append([str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute), klines[-1]])
                        else:
                            data[top_300_futures_usdt_name] = [[str(year) + '-' + str(month) + '-' + str(day) + ' ' + str(hour) + ':' + str(minute), klines[-1]]]

                        with open(json_file_path, 'w', encoding='utf-8') as file:
                            json.dump(data, file, indent=4)

                    time.sleep(0.1)
                    bar_for_volume.update(j + 1)
                bar_for_volume.finish()

                # save klines_list
                klines_list_filename = "klines/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_contract.json'
                with open(klines_list_filename, "w") as json_file:
                    json.dump(klines_list, json_file, indent=4)
            
            # 輸出得到K線資料
            # 印出年、月、日、小時和分鐘在同一行
            print(f"{year}年 {month}月 {day}日 {hour}：{minute}")
            binance_json_filename = "data/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_spot.json'
            with open(binance_json_filename, "w") as json_file:
                json.dump(top_300_usdt_pairs, json_file, indent=4)

            binance_json_filename = "data/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_contract.json'
            with open(binance_json_filename, "w") as json_file:
                json.dump(top_300_futures_usdt_pairs, json_file, indent=4)
            
        # 檢查分鐘是否是 15 的倍數，15 分鐘更新一次
        if current_time.tm_min % 15 == 0:
            # 拿幣安合約成交量前 300 名的資料            
            top_100_usdt_pair_names = top_300_futures_usdt_pair_names[:100]

            # 拿這些幣的合約資料
            top_100_usdt_pair_informations = {} 
            print("get top 100 usdt pairs...")
            bar_for_coinglass.start()
            for i in range(len(top_100_usdt_pair_names)):
                pair = top_100_usdt_pair_names[i]

                main_coin = pair.replace("USDT", "")
                base_coin = "USDT"
                
                # get perpetual market informations
                perpetual_market = coinglass_api.get_perpetual_market(main_coin)
                time.sleep(2)
                try: 
                    coin_informations = perpetual_market['data'][main_coin][0]
                    top_100_usdt_pair_informations[pair] = coin_informations
                except:
                    pass

                bar_for_coinglass.update(i + 1)
            bar_for_coinglass.finish()

            perp_json_filename = "data/" + str(year) + '_' + str(month) + '_' + str(day) + '_' + str(hour) + '_' + str(minute) + '_coinglass.json'
            with open(perp_json_filename, "w") as json_file:
                json.dump(top_100_usdt_pair_informations, json_file, indent=4)

            # 檢查資金費率
            funding_rate.analyze_funding_rate_and_report(top_100_usdt_pair_informations)

        # 等待 30 秒，避免無限迴圈過於頻繁
        time.sleep(30)