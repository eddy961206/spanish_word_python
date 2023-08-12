from scrap import scrape_website
import mysql.connector
import requests
import json
import os

def insert_data(data):

    # MySQL에 연결
    connection = mysql.connector.connect(
        host=os.environ.get('MYSQL_DB_HOST'),   # 환경 변수에서 정보를 불러옴
        user=os.environ.get('MYSQL_DB_USER'),
        password=os.environ.get('MYSQL_DB_PW'),
        database="spanish_app"
    )

    cursor = connection.cursor()

    # words 테이블 생성 (이미 존재한다면 이 부분을 건너뛸 수 있음)
    # cursor.execute("""
    # CREATE TABLE words (
    #     word_id INT AUTO_INCREMENT PRIMARY KEY,
    #     main_title VARCHAR(255),
    #     sub_title VARCHAR(255),
    #     spanish_word VARCHAR(255) NOT NULL,
    #     english_word VARCHAR(255) NOT NULL,
    #     korean_word VARCHAR(255)
    # )
    # """)

    # 중복된 스페인어 단어를 확인하기 위한 set
    seen = set()

    headers = {
        "X-Naver-Client-Id": os.environ.get('PAPAGO_CLIENT_ID'),
        "X-Naver-Client-Secret": os.environ.get('PAPAGO_CLIENT_SECRET')
    }
    
    # 데이터 삽입
    for row in data:
        # 스페인어 단어가 이미 확인된 단어인지 확인
        if row[2] not in seen:
            # 확인되지 않은 단어라면 DB에 삽입하고, 확인된 단어 set에 추가
            query = """
            INSERT INTO words (main_title, sub_title, spanish_word, english_word)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, row)
            seen.add(row[2])
            # 영어 단어를 한국어로 번역
            try:
                data = {
                    "source": "en",
                    "target": "ko",
                    "text": row[3]
                }
                response = requests.post("https://openapi.naver.com/v1/papago/n2mt", headers=headers, data=data)
                response.raise_for_status()
                
                translated_text = json.loads(response.text)['message']['result']['translatedText']
                
                # 번역된 단어를 korean_word 컬럼에 추가
                # cursor.execute("UPDATE words SET korean_word = :1 WHERE english_word = :2", (translated_text, row[3])) # 오라클 방식
                cursor.execute("UPDATE words SET korean_word = %s WHERE english_word = %s", (translated_text, row[3]))  # MySQL 방식

            except requests.exceptions.RequestException as e:
                print(f"번역 실패 단어 : {row[3]}: {e}")


    # 변경사항 저장
    connection.commit()

    cursor.close()
    connection.close()
    print("데이터 INSERT가 완료됐습니다.")

data = scrape_website()
insert_data(data)