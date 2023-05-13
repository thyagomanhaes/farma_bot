import requests

CANAL_NOTIFICACOES_BETFAIR = "1001412054755"


def send_message_to_telegram(message, channel):
    try:
        message_sent = requests.get(
            "https://api.telegram.org/bot896947138:AAH5NQ9aOajFKrRPXC8tlIX96rpjvgWbqJI/sendMessage?chat_id=-" + channel
            + "&text={}&parse_mode=html".format(
                message))
        return message_sent
    except Exception as error:
        print("Error sending menssage to Telegram: ", error)