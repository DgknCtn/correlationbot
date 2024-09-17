import requests

CHART_SERVER_URL = 'http://127.0.0.1:5001/get_chart'

try:
    response = requests.post(CHART_SERVER_URL, json={'symbol': 'BTC'})
    if response.status_code == 200:
        print("Grafik başarıyla alındı.")
        print("Yanıt:", response.json())
    else:
        print("Grafik sunucusuna bağlanılamadı.")
except requests.exceptions.RequestException as e:
    print("Hata oluştu:", e)
