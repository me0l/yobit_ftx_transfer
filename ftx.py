from json import dump, load
from time import sleep, time
from requests import Session, Request
from hmac import new
from os.path import isfile


def _prepare_request(request: Request, api_key: str, secret_key: str):
    prepared = request.prepare()

    ts = int(time() * 1000)
    payload = f"{ts}{prepared.method}{prepared.path_url}".encode() + prepared.body

    signature = new(
            secret_key.encode(),
            payload,
            "sha256").hexdigest()

    request.headers["FTX-KEY"] = api_key
    request.headers["FTX-SIGN"] = signature
    request.headers["FTX-TS"] = str(ts)

    return request


def request_withdrawal(
        api_key: str,
        secret_key: str,
        coin: str,
        size: int,
        address: str,
        method: str = "bep2"):
    session = Session()
    request = Request("POST", "https://ftx.com/api/wallet/withdrawals", json={
            "coin": coin,
            "size": size,
            "address": address,
            "method": method
        })
    request = _prepare_request(request, api_key, secret_key)

    return session.send(request.prepare()).json()


def main():
    if not isfile("ftx_api.json"):
        api_key = input("Введите апи ключ -> ")
        secret_key = input("Введите секретный ключ -> ")

        dump(
            {"api_key": api_key, "secret_key": secret_key},
            open("ftx_api.json", "w+")
            )
    ftx_api = load(open("ftx_api.json", "r+"))

    api_key = ftx_api["api_key"]
    secret_key = ftx_api["secret_key"]

    method = input("Введите сеть валюты -> ")
    coin = input("Введите валюту -> ")
    size = input("Введите количество приобретаемой валюты -> ")
    address_path = input("Введите путь до файла с кошельками для отправки -> ")

    addresses = open(address_path, "r+").read().strip().split("\n")

    for address in addresses:
        print(request_withdrawal(api_key, secret_key, coin, int(size), address, method))
        sleep(1)


main()
