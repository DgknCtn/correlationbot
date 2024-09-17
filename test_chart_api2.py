import requests

def test_chart_api():
    CHART_SERVER_URL = 'http://localhost:5001/get_chart'
    symbol = 'BTCUSDT'  # İstediğiniz bir coin sembolünü kullanabilirsiniz
    response = requests.post(CHART_SERVER_URL, json={'symbol': symbol})
    print(f"Yanıt Kodu: {response.status_code}")
    try:
        response_json = response.json()
        print(f"Yanıt JSON'u: {response_json}")
    except ValueError:
        print("Yanıt JSON formatında değil.")

if __name__ == '__main__':
    test_chart_api()
