import json, requests, config
from flask import Flask, request, jsonify, render_template
from telethon.sync import TelegramClient
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging
from binance.error import ClientError

default_marginType = 'ISOLATED'
default_leverage = 5

config_logging(logging, logging.DEBUG)

def telegram_bot_sendtext(bot_message):
    bot_token = config.TELEGRAM_API
    test_tvID = config.TEST_TV_ID

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
        print('quantity:', quantity, float(round(quantity/self.ratio, 1)))

        if symbol == 'BTCUSDT' or symbol == 'ETHUSDT' or symbol == 'BNBUSDT':
            new_quantity = float(round(quantity/self.ratio, 3))

        if symbol == 'OPUSDT' or symbol == 'APTUSDT':
            new_quantity = float(round(quantity/self.ratio, 1))

        if symbol == 'DOGEUSDT' or symbol == 'ADAUSDT' or symbol == 'MATICUSDT' or symbol == 'ZILUSDT':
            new_quantity = float(round(quantity/self.ratio))

        # self.change_margin_type(symbol, default_marginType)
        # self.change_leverage(symbol, default_leverage)

        print(symbol, side, new_quantity, position_side)

        response = None
        try:
            logging.info(new_quantity)
            response = self.um_futures_client.new_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=new_quantity,
                positionSide=position_side
            )
            logging.info(response)

            # 檢查 response 是不是有問題
            if "msg" in response and response["msg"] == "Unknown error, please check your request or try again later.":
                telegram_bot_sendtext("幣安 API 有問題，請人工檢查一下！")

            if "msg" in response and response["msg"] == "Internal error; unable to process your request. Please try again.":
                telegram_bot_sendtext("幣安 API 有問題，請人工檢查一下！")

        except ClientError as error:
            logging.error(
                "Found error. status: {}, error code: {}, error message: {}".format(
                    error.status_code, error.error_code, error.error_message
                )
            )

        return response

app = Flask(__name__)

@app.route('/')
def welcome():
    return "Hello world!"

@app.route('/webhook', methods=['POST'])
def webhook():
    print("---------------------------- receive a order from TV")
    print(" ")

    # init client
    kai_client = WhosClient(config.API_KEY, config.API_PRIVATE_KEY, 100)
    import time
    time.sleep(3)
    su_client = WhosClient(config.SU_API_KEY, config.SU_API_PRIVATE_KEY, 200)

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

    print("---------------------------- order su's trade")
    print(" ")
    order_response = su_client.order(symbol, side, quantity, market_position)

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
    