import config
import requests

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


class DetermineTOPN():
    def __init__(self, futures_or_not):
        self.futures_or_not = futures_or_not
        self.last_top_N_usdt_pair_names = None
        self.last_top_300_usdt_pair_names = None

    def compare_with_last_time(self, top_N_usdt_pair_names, top_300_usdt_pair_names):
        # 跟上次的結果比較多了哪些新幣
        if self.last_top_N_usdt_pair_names == None:
            self.last_top_N_usdt_pair_names = top_N_usdt_pair_names
            self.last_top_300_usdt_pair_names = top_300_usdt_pair_names
        else:
            # 比較舊的跟新的多了那些 pair
            for i in range(len(top_N_usdt_pair_names)):
                pair = top_N_usdt_pair_names[i]
                if pair not in self.last_top_N_usdt_pair_names:
                    try:
                        last_index = self.last_top_300_usdt_pair_names.index(pair)
                        print("這次新增: ", pair, " 是第 ", i, " 名")
                        print(pair, "在上一輪是第", last_index, "名")
                    except:
                        last_index = 999
                        print("上次不在前 300 名裡，這次是第 ", i, " 名")
                    
                    # 如果上升三名才回報
                    if last_index - i >= 3:
                        telegram_bot_sendtext("這次新增: " + pair + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名")
            print("\n")
            self.last_top_N_usdt_pair_names = top_N_usdt_pair_names
            self.last_top_300_usdt_pair_names = top_300_usdt_pair_names

    def compare(self, top_300_usdt_pair_names, top_300_usdt_pair_pricechangepercent):
        if self.last_top_300_usdt_pair_names == None:
            self.last_top_300_usdt_pair_names = top_300_usdt_pair_names
        else:
            for i in range(len(top_300_usdt_pair_names)):
                if top_300_usdt_pair_names[i] in self.last_top_300_usdt_pair_names:
                    # 比較上升了幾名
                    last_index = self.last_top_300_usdt_pair_names.index(top_300_usdt_pair_names[i])
                    # 上升 5 名以上，不在前 100 名，就回報
                    if last_index - i >= 5 and last_index > 100:
                        if self.futures_or_not:
                            telegram_bot_sendtext("合約部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))
                            print("合約部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))
                        else:
                            telegram_bot_sendtext("現貨部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))
                            print("現貨部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))

                else:
                    # 表示是新進榜的
                    last_index = 999
                    if self.futures_or_not:
                        telegram_bot_sendtext("合約部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))
                        print("合約部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動" + str(top_300_usdt_pair_pricechangepercent[i] + "%"))
                    else:
                        telegram_bot_sendtext("現貨部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))
                        print("現貨部分，這次新增: " + top_300_usdt_pair_names[i] + " 是第 " + str(i) + " 名" + "，在上一輪是第" + str(last_index) + "名，上升" + str(last_index - i) + "名，變動 " + str(top_300_usdt_pair_pricechangepercent[i] + " %"))

            self.last_top_300_usdt_pair_names = top_300_usdt_pair_names