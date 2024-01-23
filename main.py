import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
import time
import re
import requests
import datetime

def _load_driver():
        """
        driver の起動
        """
        options = webdriver.chrome.options.Options()
        options.add_argument('--headless')  # headlessモードを有効にする

        chrome_service = fs.Service()
        driver = webdriver.Chrome(service=chrome_service, options=options)
        driver.implicitly_wait(15)

        return driver

def send_line_notification(message):
    """
    LINE Notifyを使ってLINEに通知を送る
    """
    line_token = "nNB2yrfWAW6SKIRSMN08OoSQi6aZiRuZRMQNeEMFgOS"
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_token}'}
    data = {'message': f'{message}'}
    requests.post(line_notify_api, headers=headers, data=data)

def extract_floor_number(text):
    # 正規表現を用いて階数を含む部分を探す
    match = re.search(r'(\d+)階', text)
    if match:
        # 階数を整数型で返す
        return int(match.group(1))
    else:
        # 階数が見つからなかった場合はNoneを返す
        return None

def extract_specific_layout_type(text):
    # 特定の間取りパターンに一致するかチェック
    pattern = r'1DK\+S|1LDK|2DK|2LDK'
    match = re.search(pattern, text)
    if match:
        # マッチした間取りタイプを返す
        return match.group(0)
    else:
        # マッチしない場合はNoneを返す
        return None

def main():
    driver = None
    while True:
        try:
                driver = _load_driver()
                driver.get("https://www.kousha-chintai.com/search/list.php?ot=_b&kw=%E3%83%95%E3%83%AD%E3%83%BC%E3%83%AB%E6%A8%AA%E6%B5%9C%E4%B8%89%E3%83%84%E6%B2%A2")
                driver.find_element(By.CLASS_NAME, "accordion-btn").click()
                time.sleep(2)
                vacancies = driver.find_elements(By.CLASS_NAME, "vacancy_box")

                for vacancy in vacancies:
                        title = vacancy.find_element(By.CLASS_NAME, "vacancy_title").text
                        madori_text = vacancy.find_elements(By.TAG_NAME, "dd")[2].text

                        floor = extract_floor_number(title)
                        madori = extract_specific_layout_type(madori_text)

                        # if floor >= 2 and madori in ["2DK", "2LDK"]:
                        if madori in ["2LDK"] or (floor >= 2 and madori in ["2DK", "2LDK"]):
                                send_text = f"""
                                [物件名] {title}
                                [階数] {floor}階
                                [間取り] {madori}
                                """
                                send_line_notification(send_text)

                driver.quit()
                print("[処理結果]: OK [処理時刻]", datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"))
                time.sleep(60)
        except Exception as e:
                print(e)
                send_line_notification("エラーが発生中！")
                if driver:
                        driver.quit()

if __name__ == "__main__":
      main()