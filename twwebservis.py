from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import base64
import time

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('chart.html')

@app.route('/get_chart', methods=['POST'])
def get_chart():
    symbol = request.json['symbol']
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get(f"https://www.tradingview.com/chart/?symbol={symbol}")
        
        # Wait for the chart to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "chart-container"))
        )
        
        # Give some extra time for the chart to fully render
        time.sleep(5)
        
        # Take a screenshot
        chart = driver.find_element(By.CLASS_NAME, "chart-container")
        screenshot = chart.screenshot_as_png
        
        # Encode the image
        encoded_image = base64.b64encode(screenshot).decode('utf-8')
        
        return jsonify({'image': encoded_image})
    
    finally:
        driver.quit()

if __name__ == '__main__':
    app.run(debug=True)
