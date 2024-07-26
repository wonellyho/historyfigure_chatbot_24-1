import tkinter as tk
from tkinter import scrolledtext
from tkinter import *
from PIL import ImageTk, Image
import webbrowser 

import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
from dotenv import load_dotenv

# chat gpt api키 불러오기
load_dotenv()
openai.api_key = os.getenv("GPT_API_KEY")

# 셀레니움 크롤링 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 셀레니움으로 네이버 지식백과 정보를 동적 웹크롤링하는 함수
def get_historical_figure_info(Q_name):
    driver = webdriver.Chrome(service=Service(), options=chrome_options)
    url = f"https://terms.naver.com/search.naver?query={Q_name}"
    driver.get(url)
    
    try:
        element = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/ul/li[1]/div[2]/div[1]/strong/a')
        element.click()
        p_tags = driver.find_elements(By.XPATH, '/html/body/div[1]/div[3]/div[1]/div[2]/div[2]/p')
        combined_text = " ".join([p_tag.text for p_tag in p_tags])
    except Exception as e:
        combined_text = "정보를 찾을 수 없습니다."
    driver.quit()
    
    return combined_text

# 답변 생성 및 답변 추출 함수
def generate_response(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response['choices'][0]['message']['content']

# gpt 서버와 소통 및 채팅창에 답변 생성 함수
def send_message():
    user_message = user_entry.get()
    if user_message:
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, "나: " + user_message + "\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.yview(tk.END)
        
        user_entry.delete(0, tk.END)
        
        messages.append({"role": "user", "content": user_message})
        response = generate_response(messages)
        messages.append({"role": "assistant", "content": response})
        
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"{Q_name}: " + response + "\n\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.yview(tk.END)

# 대화시작 버튼 기능 함수
def start_conversation():
    global Q_name, combined_text, messages, chat_display, user_entry
    
    Q_name = name_entry.get()
    combined_text = get_historical_figure_info(Q_name)
    
    messages = [
        {"role": "system", "content": f"지금부터 당신은 {Q_name}입니다. 실제 {Q_name}이 답변하는 듯이 답변해주세요. 1인칭으로 답변 부탁드립니다. 존댓말로 답변 부탁드립니다. \
        답변을 처음 시작할 때, 자기소개 없이 질문에 대한 답변을 해주세요. 답변은 80자 이내로 부탁드립니다. 제가 드린 정보에 기반해서 답변해주세요. 정보는 다음과 같습니다. {combined_text}"}
    ]
    
    # 채팅 창 생성
    chat_window = tk.Toplevel(root)
    chat_window.title("채팅창")
    
    chat_display = scrolledtext.ScrolledText(chat_window, width=70, height=40, state=tk.DISABLED)
    chat_display.pack(pady=10)
    
    user_entry = tk.Entry(chat_window, width=65)
    user_entry.pack(side=tk.LEFT, padx=(10, 0), pady=(0, 10), ipady=20)

    send_button = tk.Button(chat_window, text="전송", command=send_message)
    send_button.pack(side=tk.LEFT, padx=(10, 10), pady=(0, 10))

    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, f"안녕하세요 저는 {Q_name} 이에요. 저에 대해 어떤 것이 궁금하죠?\n\n")
    chat_display.config(state=tk.DISABLED)
    chat_display.yview(tk.END)
    
    chat_window.mainloop()

def create_image_with_text(parent, image_path, title, description):

    image = PhotoImage(file=image_path).subsample(3, 3)
    frame = Frame(parent, bg="white")
    image_label = Label(frame, image=image, bg="white")
    image_label.image = image 
    image_label.pack(side="left", padx=5, pady=0)

    text_frame = Frame(frame, bg="white")
    title_label = Label(text_frame, text=title, font=("Arial", 10, "bold"), bg="white")
    title_label.pack(anchor="w")
    description_label = Label(text_frame, text=description, font=("Arial", 9), bg="white")
    description_label.pack(anchor="w")
    text_frame.pack(side="left", padx=5, pady=0)

    frame.pack(pady=5) 

# 국립고궁박물관 교육영상 사이트 연결 함수
def open_museumsite():
    webbrowser.open("https://www.gogung.go.kr/gogung/bbs/BMSR00090/list.do?menuNo=800062")

# 화면 구성
root = Tk()
root.title("역사인물 Talk")

bg_image_path = "그림1.jpg"
bg_image = Image.open(bg_image_path)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = Canvas(root, width=bg_image.size[0], height=bg_image.size[1])
canvas.pack()

canvas.create_image(0, 0, anchor="nw", image=bg_photo)

title_label = Label(root, text="역사인물 Talk", font=("궁서", 20), bg="white")
title_label.place(relx=0.5, rely=0.1, anchor="center")

label = Label(root, text="추천 친구:", font=("Arial Rounded MT Bold", 9, "bold"), bg="white")
label.place(relx=0.5, rely=0.18, anchor="center")

image_frame = Frame(root, bg="white")
image_frame.place(relx=0.5, rely=0.4, anchor="center")

# 추천인물 & 상태메세지
create_image_with_text(image_frame, "kg.png", "김구", "'어둠이 지나야 새벽이 온다'")
create_image_with_text(image_frame, "sj.png", "세종대왕", "       '나라사랑 백성사랑'       ")
create_image_with_text(image_frame, "ydj.png", "윤동주", "'죽는 날까지 하늘을 우러러\n 한 점 부끄럼이 없기를'")

label = Label(root, text="대화하고 싶은 인물을 입력하시오:", font=("Arial Rounded MT Bold", 13), bg="white")
label.place(relx=0.5, rely=0.7, anchor="center")

name_entry = Entry(root, width=40)
name_entry.place(relx=0.5, rely=0.75, anchor="center")

start_button = Button(root, text="대화시작",command=start_conversation)
start_button.place(relx=0.5, rely=0.8, anchor="center")

museum_button=Button(root,text="더 알아보기",command=open_museumsite)
museum_button.place(relx=0.8, rely=0.95, anchor="w")

root.mainloop()
