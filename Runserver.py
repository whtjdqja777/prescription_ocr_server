from fastapi import FastAPI, UploadFile, File #FastAPI: 웹API를 정의하는 앱 객체, UploadFile: 클라이언트가 업로드한 파일을 표현 하는 객체 타입, 업로드된 바이트 파일을 받아오는 역할, 
#File(...)이 파라미터를 multipart/form-data의 파일로 받아오라고 FastAPI에 선언, 파일을 받올 위치와 조건을 선언
# from runocr import RunOcr
import numpy as np
import cv2
from typing import Dict
from Paddle_ocr import prescription_ocr
app = FastAPI() #FastAPI 객체 선언
#ocr을 수행할 객체 생성
#그냥 객체 생성안하고 prescription_ocr.grid_predict(img)로 쓰면 인자로 self부분까지 넘겨야되서 오류 발생함

prescription_ocr_inst =  prescription_ocr()
#유저관리용 URL: @app.get("/users/{user_id}")

#품목관리
@app.get("/items/{item_id}")
def return_item(item_id: int, item_name: str):
    return {"message": "Hello FastAPI"}

@app.post("/Paddle_OCR") #"/Paddle_OCR"로 요청이 왔을때 실행
#이거 종료해도 프로세스 안닫아서 프로세스 킬 시켜줘야함
#cmd에서 
#netstat -ano | findstr :8000으로 8000포트 사용하고 있는 프로세스 찾고
#taskkill /PID 19828 /F 로 킬해줘야함
#async 비동기로 선언
async def reponse_of_Paddle_OCR(image_file: UploadFile = File(...)): #image_file받아온 파일이 저장될 변수
                                            #UploadFile 업로드된 바이트파일을 가져오는 역할
                                            #File(...) 이곳에 파일을 보내고 (...)은 반드시 파일이 있어야한다는 뜻 (None)는 없어도 상관 없다는 뜻
    print("수신")
    print("파일이름", image_file.filename)
    print("파일타입", image_file.content_type)
    img_file = await image_file.read()# image_file.read()등 I/O작업은 시간이 오래걸려 해당 시간 동안 CPU낭비가 있음
    #await을 선언하면 image_file.read()라는 I/O 작업을 하는 동안 CPU가 다른 요청/연산 작업을 할 수 있게 하여 CPU 낭비를 줄여줌
    #image_file.read()작업이 완료되면 다시 이어서 실행됨 
    #CPU는 엄청 빠른데 I/O는 CPU에 비해 매우느리기 때문에 I/O같은 시간이 오래걸리는 작업에는 await을 선언해 줘야됨
    #await 선언 X -> 동기: 해당 작업을 끝낼때까지 다른거 못함, await선언 -> 비동기: 다른 작업 가능 -> 여러요청 처리 가능
    #imgage_file.read()의 read()는 원래 비동기 메서드라서 await선언이 필수임 !!!
    nparr = np.frombuffer(img_file, np.uint8) # Buffer는 임시 저장 공간이 여기에선 img_file이 버퍼임 
    #unit8로 변환해주는 이유가 FastAPI는 바이트로 받아오기 때문에 처리하기 적절한 형태로 변환이 필요(client에서 파일 업로드할때로 byte 형태로 바꿔서 업로드함) 
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #B,G,R 숫자 배열을 이미지로 디코딩
    print(img)
    if img is None:
        print("디코딩 실패")
        return {"error": '디코딩 실패'}
    else:
        print('ocr 시작')
        table = prescription_ocr_inst.grid_predict(img)
        if table: 
            Dosage, drug_info = prescription_ocr_inst.extract_element(table)
            result = {'Dosage': Dosage, 'drug_info': drug_info}
        
            return result
        else:
            print("격자 인식 실패")
            return []

@app.post('/complex_synthesis')
async def reponse_of_complex_synthesis(drugs: Dict): # json형태로 받기 위해 typing의 Dict 사용
    # 상호작용 검사 코드
    print(drugs)
    complex_synthesis = {'data': '주의 필요'}

    return complex_synthesis


