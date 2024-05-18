import os.path
import numpy as np
from fastapi import FastAPI
import uvicorn
import fastapi.responses
import io
from fastapi import Form,File,UploadFile
from typing import List
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import hashlib
from PIL import Image, ImageDraw, ImageEnhance
import matplotlib.pyplot as plt
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
import uvicorn
from PIL import Image
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root(request: Request):
 return templates.TemplateResponse("index.html", {"request": request})
@app.post("/")
async def check(request: Request ):
    return templates.TemplateResponse("forms.html",{"request": request,"ready": False, "images": []})

@app.post("/image_form", response_class=HTMLResponse)
async def make_image(request: Request, n: int = Form(), files: List[UploadFile] = File(description="Multiple files as UploadFile")):
#посылаем post запрос на сайт Google для проверки прохождения Captcha
    ready = False
    print(len(files))
    if (len(files) > 0):
        if (len(files[0].filename) > 0):
            ready = True
            images = []
            if ready:
                    print([file.filename.encode('utf-8') for file in files])
                    #преобразуем имена файлов в хеш -строку
                    images = ["static/" + hashlib.sha256(file.filename.encode('utf-8')).hexdigest()for file in files]
                    # берем содержимое файлов
                    content = [await file.read() for file in files]
                    # создаем объекты Image типа RGB размером 200 на 200
                    p_images = [Image.open(io.BytesIO(con)).convert("RGB").resize((200, 200))for con in content]
                    for i in range(len(p_images)):

                        width, height = p_images[i].size  # размеры изображения
                        # координаты для разделения изображения на две половины
                        mid_x = width // 2
                        mid_y = height // 2

                        if n == 1:
                            # Разделяем изображение на две половины
                            left_half = p_images[i].crop((0, 0, mid_x, height))
                            right_half = p_images[i].crop((mid_x, 0, width, height))

                            # Меняем местами левую и правую половины
                            swapped_image = Image.new('RGB', (width, height))
                            swapped_image.paste(right_half, (0, 0))
                            swapped_image.paste(left_half, (mid_x, 0))
                        else:
                            # Разделяем изображение на две половины
                            top_half = p_images[i].crop((0, 0, width, mid_y))
                            bottom_half = p_images[i].crop((0, mid_y, width, height))

                            # Меняем местами верхнюю и нижнюю половины
                            swapped_image = Image.new('RGB', (width, height))
                            swapped_image.paste(bottom_half, (0, 0))
                            swapped_image.paste(top_half, (0, mid_y))
                        # График распределения цветов исходной картинки
                        img_array_after = np.asarray(p_images[i])
                        colors, counts = np.unique(img_array_after.reshape(-1, 3), axis=0, return_counts=True)
                        plt.figure(figsize=(10, 5))
                        plt.bar(range(len(colors)), counts, color=colors / 255)
                        plt.xlabel('Цвет')
                        plt.ylabel('Количество пикселей')
                        plt.title('Распределение цветов на изображении')
                        image_1 = plt.savefig("static/image_1.png")
                        #plt.clf()
                        p_images[i]=swapped_image
                        p_images[i].save("./" + images[i], 'JPEG')


    return templates.TemplateResponse("forms.html", {"request": request,"ready": ready, "images": images})

@app.get("/image_form", response_class=HTMLResponse)
async def make_image(request: Request):
   return templates.TemplateResponse("forms.html", {"request": request})

if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1", port=8000)

'''
def swap_halves(image_path):
    image = Image.open(image_path)# Открываем изображение
    width, height = image.size # размеры изображения
    # координаты для разделения изображения на две половины
    mid_x = width // 2
    mid_y = height // 2

    if n==1:
        # Разделяем изображение на две половины
        left_half = image.crop((0, 0, mid_x, height))
        right_half = image.crop((mid_x, 0, width, height))

        # Меняем местами левую и правую половины
        swapped_image = Image.new('RGB', (width, height))
        swapped_image.paste(right_half, (0, 0))
        swapped_image.paste(left_half, (mid_x, 0))
    else:
        # Разделяем изображение на две половины
        top_half = image.crop((0, 0, width, mid_y))
        bottom_half = image.crop((0, mid_y, width, height))

        # Меняем местами верхнюю и нижнюю половины
        swapped_image = Image.new('RGB', (width, height))
        swapped_image.paste(bottom_half, (0, 0))
        swapped_image.paste(top_half, (0, mid_y))
    return swapped_image
image_path = 'D:/ФОТО Redmi 9T/Камера/Flower.jpg'
print("Введите 0 или 1 в соответствии с нужной вам операцией")
print("Какие части изображения поменять?")
n=int(input("0—верхнюю и нижнюю, 1—правую и левую"))
swapped_image = swap_halves(image_path) # Меняем местами половины изображения
swapped_image.show()
'''