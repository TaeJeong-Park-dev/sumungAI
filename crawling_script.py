import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import base64
import fitz
import io
import os

categories = {'19':'학사','20':'일반', '21':'사회봉사', '22':'등록_장학', '189':'학생생활', '190':'글로벌', '162':'진로취업', '420':'비교과'}

def crawl_and_save():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9211")
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=options)
    
    today = datetime.today().strftime('%Y-%m-%d')
    start = today
    end = today

    for data in categories:
        count = 0  
        url = f'https://www.smu.ac.kr/kor/life/notice.do?srUpperNoticeYn=on&srStartDt={start}&srEndDt={end}&mode=list&srCategoryId1={data}&srCampus=smuc&srSearchKey=&srSearchVal=#'
        driver.get(url)
        time.sleep(1)

        route = f'공지사항/category_{categories[data]}/'
        if not os.path.exists(route):
            os.makedirs(route)

        while True:
            link_list = driver.find_elements(By.CSS_SELECTOR, 'ul td a')
            href_sub = []

            for link in link_list:
                temp = link.get_attribute('href')
                if temp not in href_sub:
                    href_sub.append(temp)

            for href in href_sub:
                driver.get(href)
                time.sleep(1)

                result = driver.execute_cdp_cmd("Page.printToPDF", {
                    "landscape": False,
                    "printBackground": True,
                    "displayHeaderFooter": False,
                    "preferCSSPageSize": True
                })
                pdf_content = base64.b64decode(result['data'])

                pdf_stream = io.BytesIO(pdf_content)
                doc = fitz.open("pdf", pdf_stream)

                first_page_crop_rect = fitz.Rect(120, 165, 612, 770)
                first_page = doc[0]
                first_page.set_cropbox(first_page_crop_rect)

                other_pages_crop_rect = fitz.Rect(120, 25, 612, 770)
                for page_num in range(1, len(doc)):
                    page = doc[page_num]
                    page.set_cropbox(other_pages_crop_rect)

                pdf_stream = io.BytesIO()
                doc.save(pdf_stream)

                path = route + categories[data] + str(count) + '.pdf'
                with open(path, 'wb') as f:
                    f.write(pdf_stream.getvalue())

                doc.close()
                count += 1

            driver.find_element(By.CSS_SELECTOR, 'ul.btn-wrap.board-text-right li a.btn.btn01').click()
            time.sleep(1)

            try:
                driver.find_element(By.CSS_SELECTOR, 'ul.paging-wrap li a.page-icon.page-next').click()
            except:
                break
        time.sleep(0.1)

    driver.quit()

if __name__ == "__main__":
    crawl_and_save()
