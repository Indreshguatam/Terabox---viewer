from flask import Flask, render_template, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import platform

app = Flask(__name__)

def kill_chrome_processes():
    try:
        if platform.system() == "Windows":
            os.system('powershell "Get-Process chromedriver -ErrorAction SilentlyContinue | Stop-Process -Force"')
            os.system('powershell "Get-Process chrome -ErrorAction SilentlyContinue | Stop-Process -Force"')
        else:
            os.system("pkill -f chromedriver")
            os.system("pkill -f chrome")
    except Exception as e:
        print(f"Error killing processes: {e}")

def get_chrome_driver():
    kill_chrome_processes()
    
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Force specific ChromeDriver version that matches your Chrome
    service = Service(ChromeDriverManager(version="114.0.5735.90").install())
    return webdriver.Chrome(service=service, options=chrome_options)

def extract_video_url(terafile_url):
    driver = None
    try:
        driver = get_chrome_driver()
        driver.get(terafile_url)
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "video"))
        )

        video_element = driver.find_element(By.TAG_NAME, "video")
        video_url = video_element.get_attribute("src")
        return video_url if (video_url and video_url.startswith("http")) else None
        
    except Exception as e:
        print(f"Error extracting video: {e}")
        return None
    finally:
        if driver:
            driver.quit()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fetch", methods=["POST"])
def fetch():
    data = request.get_json()
    link = data.get("link", "").strip().lower()

    if not link or "terafileshare.com" not in link:
        return jsonify({
            "success": False, 
            "error": "Please enter a valid TeraFileShare link (terafileshare.com)"
        })

    video_url = extract_video_url(link)
    return jsonify({
        "success": bool(video_url),
        "videoUrl": video_url,
        "error": None if video_url else "Could not extract video URL"
    })

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)  # Disable reloader to prevent multiple driver instances