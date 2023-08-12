from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os


def scrape_website():

  # 웹드라이버 설정
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')
  options.add_argument('--no-sandbox')
  options.add_argument('--disable-dev-shm-usage')

  # 크롬 드라이버 최신 버전 설정
  service = Service(executable_path=ChromeDriverManager().install())

  # chrome driver
  driver = webdriver.Chrome(service=service, options=options) # <- options로 변경


  # 웹페이지 접속
  driver.get('https://www.spanish.academy/blog/1000-most-common-spanish-words-for-beginners/')

  soup = BeautifulSoup(driver.page_source, 'html.parser')

  headings = soup.find_all('h2', class_='has-text-color nitro-offscreen')

  data = []

  for heading in headings:
      next_sibling = heading.find_next_sibling(['h3', 'ul', 'h2'])

      if ('these…' in heading.text or 'Start Today!' in heading.text):
          continue

      subheading = ""  # subheading 변수를 빈 문자열로 초기화

      while next_sibling:
          if next_sibling.name == 'h3':
              subheading = next_sibling.text.replace('\xa0', ' ')
          elif next_sibling.name == 'ul':
              li_texts = [li.text for li in next_sibling.find_all('li')]
              for item in li_texts:
                  spanish_word, english_word = item.split('—' if '—' in item else '–')
                  spanish_word = spanish_word.strip()
                  english_word = english_word.strip()
                  data.append((heading.text, subheading, spanish_word, english_word))
          elif next_sibling.name == 'h2':
              break

          next_sibling = next_sibling.find_next_sibling(['h3', 'ul','h2'])

          # print(data)
  driver.quit()
  
  return data