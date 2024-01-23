import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome import service as fs
import time
import re
import requests
import datetime
from logger import get_module_logger

logger = get_module_logger(__name__)

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
    pattern = r'1DK\+S|1LDK|2DK|2LDK|3LDK'
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
            driver.get("https://www.kousha-chintai.com/search/list.php?ot=_b&kw=%E3%83%95%E3%83%AD%E3%83%BC%E3%83%AB%E5%B1%B1%E7%94%B0%E7%94%BA+%E3%83%95%E3%83%AD%E3%83%BC%E3%83%AB%E6%A8%AA%E6%B5%9C")
            accordions = driver.find_elements(By.CSS_SELECTOR, ".title_green.accordion-btn")
            for accordion in accordions:
                accordion.click()
                time.sleep(1)

            time.sleep(2)
            vacancies = driver.find_elements(By.CLASS_NAME, "vacancy_box")

            for vacancy in vacancies:
                title = vacancy.find_element(By.CLASS_NAME, "vacancy_title").text
                madori_text = vacancy.find_elements(By.TAG_NAME, "dd")[2].text

                floor = extract_floor_number(title)
                madori = extract_specific_layout_type(madori_text)

                # 2LDK か 2階以上の2DKなら通知する
                if madori in ["2LDK"] or (floor >= 2 and madori in ["2DK"]):
                    send_text = f"[物件名] {title} \n[階数] {floor}階 \n[間取り] {madori}"
                    send_line_notification(send_text)

            driver.quit()
            logger.info("[処理結果] OK")
            time.sleep(60)
        except Exception as e:
            logger.error(f"[処理結果] NG")
            send_line_notification("エラーが発生中！")
            if driver:
                driver.quit()

if __name__ == "__main__":
      main()