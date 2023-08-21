from time import sleep

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC


class EksiScrape:
    def __init__(self, key):
        self.key = key
        self.url_login = ''
        self.headers = {
            'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'}
        self.driver = None
        self.options = None
        self.wait = None
        self.username = None
        self.password = None
        self.search = None
        self.data = []
        self.entry_ids = set()
        self.page = None
        self.current_url = None

    def start_driver(self):
        self.options = ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = Chrome(options=self.options)

    def stop_driver(self):
        if self.driver:
            self.driver.quit()

    def login(self):
        self.start_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.get("https://eksisozluk1923.com/")

    def search_key_word(self):
        self.login()
        self.search = self.wait.until(
            EC.visibility_of_element_located((By.ID, "search-textbox")))
        self.search.send_keys(self.key)
        self.search.send_keys(Keys.ENTER)

    def change_page(self, i):
        next_page = str(self.current_url) + f'?p={i}'
        return next_page

    def running(self):
        self.search_key_word()
        page_number = self.driver.find_element(By.CSS_SELECTOR, '#topic > div.clearfix.sub-title-container > div.pager > a.last').text
        self.page = int(page_number)
        self.current_url = self.driver.current_url
        self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li[id="entry-item"]')))
        page_li = self.driver.find_elements(By.CSS_SELECTOR, 'li[id="entry-item"]')
        for li in page_li:
            entry = self.get_entry_data(li)
            if entry:
                print('buradayiz')
                entry_id = ''.join(entry)
                if entry_id not in self.entry_ids:
                    self.entry_ids.add(entry_id)
                    self.data.append(entry)
        for i in range(2, int(page_number)+1):
            self.driver.get(self.change_page(i))
            sleep(2)
            self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'li[id="entry-item"]')))
            page_li = self.driver.find_elements(By.CSS_SELECTOR, 'li[id="entry-item"]')
            for li in page_li:
                entry = self.get_entry_data(li)
                if entry:
                    entry_id = ''.join(entry)
                    if entry_id not in self.entry_ids:
                        self.entry_ids.add(entry_id)
                        self.data.append(entry)
        self.save_excel()

    @staticmethod
    def get_entry_data(li):
        user = li.find_element(By.CLASS_NAME, "entry-author").text
        info = li.find_element(By.CLASS_NAME, "footer-info")
        date = info.find_element(By.CSS_SELECTOR, 'div:nth-child(2) > a').text
        entryText = li.find_element(By.CLASS_NAME, "content").text
        return user, date, entryText

    def save_excel(self):
        columns = ['from', 'date', 'entryText']
        data_dict = {column: [k[idx] for k in self.data] for idx, column in enumerate(columns)}

        dataframe = pd.DataFrame(data_dict)
        dataframe.to_excel('Eksi_1.xlsx')

        self.stop_driver()


EksiScrape('Eureko Sigorta').running()
