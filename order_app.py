import json, requests, config
from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError
import time
import subprocess

default_marginType = 'ISOLATED'
default_leverage = 10

config_logging(logging, logging.DEBUG)

def telegram_bot_sendtext(bot_message):
    bot_token = config.TELEGRAM_API
    test_tvID = config.TEST_TV_ID
    MY_TELEGRAM_ID = config.MY_TELEGRAM_ID

    # 送訊息給群組
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + test_tvID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

    return response.json()

class WhosClient:

    def __init__(self, API_KEY, API_PRIVATE_KEY, amount_per_pair):
        self.um_futures_client = UMFutures(key=API_KEY, private_key=API_PRIVATE_KEY)
        self.ratio = 10000 / amount_per_pair

    def change_margin_type(self, symbol, marginType): 
        try:
            response = self.um_futures_client.change_margin_type(
                symbol=symbol, marginType=marginType, recvWindow=6000
            )
            logging.info(response)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )
        
        return

    def change_leverage(self, symbol, leverage):
        try:
            response = self.um_futures_client.change_leverage(
                symbol=symbol, leverage=leverage, recvWindow=6000
            )
            logging.info(response)
        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

        return

    def order(self, symbol, side, quantity, position_side):
        if symbol == 'BTCUSDT' or symbol == 'ETHUSDT' or symbol == 'BNBUSDT':
            new_quantity = float(round(quantity/self.ratio, 3))

        if symbol == 'OPUSDT' or symbol == 'APTUSDT':
            new_quantity = float(round(quantity/self.ratio, 1))

        if symbol == 'DOGEUSDT' or symbol == 'ADAUSDT' or symbol == 'MATICUSDT' or symbol == 'ZILUSDT':
            new_quantity = float(round(quantity/self.ratio))

        # self.change_margin_type(symbol, default_marginType)
        self.change_leverage(symbol, default_leverage)

        print("pair: ", symbol)
        print('receive quantity:', quantity)
        print("order quantity: ", new_quantity)
        print("side: ", position_side)
        print("---------------------------- end trade")
        print(" ")

        response = None
        try:
            response = self.um_futures_client.new_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=new_quantity,
                positionSide=position_side
            )
            logging.info(response)

        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

            if error.error_message == "ReduceOnly Order is rejected.":
                telegram_bot_sendtext("幣安 API 有問題，請人工檢查一下！")

            if error.error_message == "Internal error; unable to process your request. Please try again.":
                telegram_bot_sendtext("幣安 API 有問題，請人工檢查一下！")

            if error.error_message == "Unknown error, please check your request or try again later.":
                telegram_bot_sendtext("幣安 API 有問題，請人工檢查一下！")

            return error

        return response

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Hello world!"

@app.route('/webhook', methods=['POST'])
def webhook():
    print("---------------------------- receive a order from TV")
    print(" ")

    # 要執行的命令
    command = "w32tm /resync"
    try:
        # 使用subprocess執行命令
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # 檢查命令是否成功執行
        if result.returncode == 0:
            print("命令成功執行:")
            print(result.stdout)
        else:
            print("命令執行出錯:")
            print(result.stderr)
    except Exception as e:
        print("執行命令時發生異常:", str(e))

    # init client
    kai_client = WhosClient(config.API_KEY, config.API_PRIVATE_KEY, 100) # API_KEY API_PRIVATE_KEY 你的投入資金(U)

    # 從 webhook 拿到 json
    try:
        data = json.loads(request.data)
    except:
        return {
            "code": "error input data! skip this.",
            "message": "error input data! skip this."
        }

    # 確定通行碼正確
    if data['passphrase'] != config.WEBHOOK_PASSPHRASE:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    order_response = None
    
    strategyName = data['strategyName']
    symbol = data['ticker']
    side = data['strategy']['order_action'].upper()
    quantity = data['strategy']['order_contracts']
    price = data['strategy']['order_price']
    market_position = data['strategy']['market_position'].upper()

    prev_market_position = data['strategy']['prev_market_position']
    prev_market_position_size = data['strategy']['prev_market_position_size']

    # 買入平倉 ＝ 平空
    if market_position == 'FLAT' and side == 'BUY':
        market_position = 'SHORT'
    # 賣出平倉 ＝ 平多
    if market_position == 'FLAT' and side == 'SELL':
        market_position = 'LONG'

    # send the webhook request to telegram bot
    print("---------------------------- send an order to telegram")
    print(" ")
    arrange_send_text = 'receive order from server: \n' + 'strategy: ' + strategyName + ' ' + side + ' ' + symbol + ' at ' + str(price) + ' quantity:' + str(quantity) + '\n' + 'prev market position: ' + prev_market_position + '\n' + 'prev market position size: ' + str(prev_market_position_size)
    telegram_bot_sendtext(arrange_send_text)

    print("---------------------------- order kai's trade")
    print(" ")
    order_response = kai_client.order(symbol, side, quantity, market_position)

    # 待新增判斷式，確認 order 有被正確接收
    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        print("order failed")

        return {
            "code": "error",
            "message": "order failed",
            "input_message": data
        }

if __name__ == '__main__':
	app.debug = True
	app.run()
    