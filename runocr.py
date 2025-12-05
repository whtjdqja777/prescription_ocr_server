import cv2
from  Paddle_ocr import prescription_ocr

import Levenshtein
import pandas as pd
import numpy as np

df = pd.read_excel('OpenData_ItemPermit20251127.xls')

def find_medicine():

    print(df['품목명'].head())

# img_path = 'drugs_info.png'

def RunOcr(image_file):
    
    print("RunOcr에 들어온 값 type:", type(image_file))
    try:
        print("is ndarray:", isinstance(image_file, np.ndarray))
    except Exception as e:
        print("np 관련 에러:", e)

    # 혹시 ndarray라면 shape도 출력
    if hasattr(image_file, "shape"):
        print("image_file.shape:", image_file.shape)
    padded_img = cv2.copyMakeBorder(image_file,
                                    top = 20,
                                    bottom= 20,
                                    left= 20,
                                    right= 20,
                                    borderType=cv2.BORDER_CONSTANT,
                                    value=[255,255,255,255])


    result = prescription_ocr.grid_predict(padded_img)
    tables = result.get('table_res_list', [])
    for t in tables:
        html = t['pred_html']
    # html = 
    print(result['rec_texts'])
    
    for word in result['rec_texts']:
        w2 = cal_sim(word) 
        if w2 >= 0.7:
            print(word, w2)
    return result['rec_texts']
        

    
    

def cal_sim(w2):
    w1 = '처방의약품의 명칭'
    ratio = Levenshtein.ratio(w1, w2)
    return ratio

