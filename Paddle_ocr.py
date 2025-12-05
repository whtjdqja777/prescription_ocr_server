
import cv2
from matplotlib import pyplot as plt
import re
from bs4 import BeautifulSoup
import Levenshtein
import pandas as pd
import numpy as np
from paddleocr import PPStructureV3
model = PPStructureV3(lang = 'korean')
class prescription_ocr():
    def __init__(self):
        self.grid_ocr = model
        self.Dosage = ['처방의약품의명칭', '1일투약량','1회투약량','1일투여횟수','횟수', '총투약일수','1회투여횟수','1회투여량','투약일수']
        self.name_insurance = pd.read_csv('name_insurance3.csv')
        self.drug_unit = ['정','개', 'gm', 'mg', 'mcg','mog','μg','ug' 'ng', 'mL', 'ml','mi' 'L','cc','CC'
                          'IU','회분','포','캡슐','캡슐정','스푼','ml 스푼','g','FTU']
        self.table = [['653800341 레보트로시럽', '9 cc', '3 cc', '3', '3'], ['새로딘시럽(로라타딘) 644000941', '개 1', '1 개', '1', '3'], ['유시락스시럽 654100091', '18 cc', '6 cC gm0.6667gm', '3 3', '3 3'], ['싱카스트추정5밀리그램(몬테루카 542103840', '1 정', '정', '1', '30'], ['645700564 삼아리도맥스크림', '개 1', '1 개', '1', '1']]
    def grid_predict(self, img):#격자인식 모델, Beautifulsoup의 html 파서로 행별 요소 출력
        # image = cv2.imread('prescription6.jpg')
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.imwrite('binary_to_color.png', img)
        img = self.insert_padding(img)
        result = self.grid_ocr.predict(img)
        # print(result)
        result = result[0]
        tables = result.get('table_res_list', [])   
        # print(result)
        print(type(tables))
        print(tables)

        if len(tables) >0:
            print('테이블있음')
            print(len(tables))
            for t in tables:
                
                html = t['pred_html']       # 표 전체 HTML
            print(type(html))
            print(html)
            soup = BeautifulSoup(html,'html.parser')

            table = []
            for tr in soup.find_all('tr'):
                row =[]
                for td in tr.find_all(['td','th']):
                    row.append(td.get_text(strip = True))
                if row:
                    table.append(row)
            print(table)
            return table 
        else:
            return None

# result = [['(약 국 제 출용) 의료보험 ②의료보호 ③산재보험 ④자동차보험⑤기타( ^ 요양기관기호:'], ['고부연월일및번호', '2016 년10월14일 -제00085호', '의 료 기관', '명 칭', ''], ['', '', ''], ['t', 'R 앞'], ['멕스번호', '', '주민등록번호', '090113-4******', '', '', 'e-mail주소', '', '', '', ''], ['호', 'J', '4', '5', '9', '', '처방 의료인의 성명', 
# '', '면허종별', '1Y |'], [''], ['J', '3', '0', '4', '', '면허번호'], ['처방의약품의 명칭', '1일 투약량', '1회 투약량', '1일 투여 횟수', '총 부약 일수', '$\\frac}$', '', ''], ['53800341레보트로시럽', '9 cc', '3 cc', '3', '3', '→1일2회 도포', '', '44000941새로딘시럽(로라타딘)'], ['54100091유시락스시럽', '18 cc', '6 cc', '3', '3', '', '', ''], ['45700681삼아아토크건조시럽', '2 gm', '0.6667gm', '3', '3', '', '', ''], ['12103840싱카스트추정5밀리그램(몬데무카', '1 정', '1 정', '1', '30', '', '45700564삼아리도맥스크림', '1 개'], ['', '', '', '', '', '', '', '']]
# # texts = [j for i in table for j in i]
# result = table

    def extract_element(self, table):
        return_Dosage = []
        
        return_drug_info = []
        Dosalen = 0
        
        for box in table:
            
            for inst in box:
                # print(inst)
                leninst = len(inst)
                Dosratiolist = [Levenshtein.ratio(inst.replace(" ",""), i) for i in self.Dosage]
                print(inst, Dosratiolist)
                if any(np.array(Dosratiolist) > 0.7):
                    print(Dosratiolist)
                    maxratio = max(Dosratiolist)
                    maxratio_idx = Dosratiolist.index(maxratio)            
                    return_Dosage.append(self.Dosage[maxratio_idx])
                
                elif leninst>=2:
                    
                    
                    if  re.match(r'(\d{3,})(.*)', inst.replace(" ","")):
                        inst2 = inst.replace(" ","") 
                        if inst2.isdigit() and max(Levenshtein.ratio(i,inst2) for i in self.name_insurance['보험코드']) >= 0.8 and len(inst2)>4:
                            
                            print('isdigit 실행', inst2)
                            if inst2 in self.name_insurance['보험코드'].values:
                                name = self.name_insurance.loc[self.name_insurance['보험코드'] == inst2, '품목명'].iloc[0]
                                print('if_name', name)
                            else:
                                
                                insurance_code_ratio = [Levenshtein.ratio(i, inst2) for i in self.name_insurance['보험코드']]

                                idx = insurance_code_ratio.index(max(insurance_code_ratio))

                                name = self.name_insurance.loc[idx, '품목명']
                                print('else_name', name)
                                
                            

                            find_name_idx = box.index(inst)
                            drug_info = box[find_name_idx+1:]
                            drug_info.insert(0,name)
                            return_drug_info.append(drug_info)
                        else:
                            match = re.match(r'(\d+)(.*)', inst.replace(" ",""))
                            
                            
                            
                            number, string = match.groups()
                            
                            string = string.split('(')[0].replace(" ","")
                            nameratio = [Levenshtein.ratio(name, string) for name in self.name_insurance.loc[:, '품목명']]
                            max_name_ratio = max(nameratio)
                            print(string, max_name_ratio)
                            if max_name_ratio > 0.7:
                                print('통과', string, max_name_ratio)
                                drug_info = []
                                
                                # name = self.name_insurance.loc[nameratio.index(max_name_ratio), '품목명']
                                
                                find_name_idx = box.index(inst)
                                drug_info = box[find_name_idx+1:]
                                drug_info.insert(0,string)
                                return_drug_info.append(drug_info)

                    elif re.match(r'^(.+?)(\d{3,})$', inst.replace(" ","")):
                        #싱카스트츄정5밀리그램 이거 싱카스트츄정까지만 짤라서 유사도 0.6666으로 나옴
                        #이부분 고치기
                        #러프한 방법: 대부분 보험코드하고 품목명 사이에 공백이 있기 때문에 공백을 기준으로 나눈다
                        match = re.match(r'^(.+?)(\d+)$', inst.replace(" ",""))
                        
                        
                        string, number = match.groups()
                         
                        string = string.split('(')[0].replace(" ","")
                        nameratio = [Levenshtein.ratio(name, string) for name in self.name_insurance.loc[:, '품목명']]
                        max_name_ratio = max(nameratio)
                        print(string, max_name_ratio)
                        if max_name_ratio > 0.7:
                            print('통과', string, max_name_ratio)
                            drug_info = []
                            
                            # name = self.name_insurance.loc[nameratio.index(max_name_ratio), '품목명']
                            
                            find_name_idx = box.index(inst)
                            drug_info = box[find_name_idx+1:]
                            drug_info.insert(0,string)
                            return_drug_info.append(drug_info)
                    

                    else:
                        
                    
                       
                        string = inst
                        string = string.split('(')[0].replace(" ","")
                        nameratio = [Levenshtein.ratio(name, string) for name in self.name_insurance.loc[:, '품목명']]
                        max_name_ratio = max(nameratio)
                        
                        print(string, max_name_ratio)
                        if max_name_ratio > 0.7:
                            print('통과', string, max_name_ratio)
                            drug_info = []
                            
                            # name = self.name_insurance.loc[nameratio.index(max_name_ratio), '품목명']
                            
                            find_name_idx = box.index(inst)
                            drug_info = box[find_name_idx+1:]
                            drug_info.insert(0,string)
                            return_drug_info.append(drug_info)
                
                

        return_drug_info = [i[:len(return_Dosage)] for i in return_drug_info]
        print(return_drug_info)
        print(return_Dosage)
        for i in range(len(return_drug_info)):
            for j in range(len(return_drug_info[i])):
                if re.match(r'(.+?)(\d+)$', return_drug_info[i][j].replace(" ","")):
                        print("조건 포인트:", return_drug_info[i][j])
                        match = re.match(r'(.+?)(\d+)$', return_drug_info[i][j].replace(" ",""))
                        s, t = match.groups()
                        print('1')
                        if s in self.drug_unit:
                            
                            return_drug_info[i][j] = t+s
        print(return_drug_info)
        print(return_Dosage)
        return return_drug_info, return_Dosage 
    
    def insert_padding(self,img): #패딩 주는 함수
        padded_img = cv2.copyMakeBorder(img,
                                    top = 20,
                                    bottom= 20,
                                    left= 20,
                                    right= 20,
                                    borderType=cv2.BORDER_CONSTANT,
                                    value=[255,255,255,255])
        return padded_img
    
    def dotted_line_to_line(self,img3):
        gray = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
        
        binary = cv2.adaptiveThreshold(src = gray, 
                                        maxValue= 255, #임계값을 넘으면 255로 매핑 
                                        adaptiveMethod= cv2.ADAPTIVE_THRESH_MEAN_C,#임계값을 정하는 메소드로 cv2.ADAPTIVE_THRESH_MEAN_C 는 주편 픽셀들의 밝기의 평균으로 임계값을 정함 또한 - C로 임계값 보정함  
                                        thresholdType= cv2.THRESH_BINARY_INV, #thresh_binary_"inverse" 반전된 바이너리를 출력 -> 이후 사용할 morphology가 255영역을 기준으로 연산하기 때문에 
                                                                            #그냥 바이너리 출력하면 배경: 255(흰색), 숫자,선,점선 -> 0(검정색)이기 때문에 우리는 점선을 강화해야되서 binary_inverse로 출력하도록하는 것
                                        blockSize= 15, #adaptiveMethod가 임계값을 계산할 영역 15x15 픽셀
                                        C=10 #임계값 보정값
                                        #임계값이 계산되는 방법: block_size 15x15 에서 adaptiveMethod의 ADAPTIVE_THRESH_MEAN_C로 평균을 구하고 -C를 해서 임계값을 구한다.
                                        #결국 주변 필셀들의 평균 밝기를 기준으로 0 또는 255로 매핑하는 함수 -> 검정색은 더 검정색으로, 흰색은 더 흰색으로
                                       )
        cv2.imwrite('binary_gray_output.png', cv2.bitwise_not(binary))

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))#(모양(cv2.MORPH_RECT:정사각형 커널), 크기(3,3)))
        #MORPH_RECT의 MORPH는 형태학이라는 의미 MORPH_RECT는 형태학적 정사각형을 의미
        closed = cv2.morphologyEx(src = binary, op = cv2.MORPH_CLOSE, kernel = kernel, iterations=2)
                                #src: 강화할 바이너리 이미지
                                #op: 적용할 연산 -> MORPH_CLOSE: 빈틈을 메우고 끊어진 구조를 복원하는 것을 목적으로 하는 연산
                                #윤곽 복원, 빈틈 메우기, 끊어진 선 연결 등
                                #MORPH_CLOSE: dilation -> erosion
                                # dilation(팽창)으로 픽셀을 팽창하여 점선을 붙이고 erosion(침식)하여 선의 크기를 복원(픽셀크기를 줄임): 이미 붙어버린 픽셀에 대해서는 erosion해도 붙은 상태가 유지됨 
                                #kernel = 이미지를 돌면서 연산할 커널(바운딩 박스) 입력
                                # iterations: 적을 수록 과도한 팽창/수축이 일어나지 않음 
        h, w = closed.shape
        hor_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (w//40, 1))
        ver_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, h//40))


        horiziontal = cv2.erode(closed, hor_kernel, iterations=1)
        horiziontal = cv2.dilate(horiziontal, hor_kernel, iterations=1)

        vertical = cv2.erode(closed, ver_kernel, iterations=1)
        vertical = cv2.dilate(vertical, ver_kernel, iterations=1)
        
        lines = cv2.bitwise_or(horiziontal, vertical)

        result = cv2.bitwise_not(lines) 
        # cv2.imwrite("output2.png", result)
        closed = cv2.bitwise_not(closed)
        cv2.imwrite("output.png", closed)
        print(result)
        return binary
model = prescription_ocr()

# test_extract.extract_element(test_extract.table)



# img = cv2.imread('raw_gray_output.png')
# table = model.grid_predict(img)

# model.extract_element(table)

while True:
    try:
        img_name = input()
        prescription = cv2.imread(img_name)
        prescription = cv2.cvtColor(prescription, cv2.COLOR_BGR2GRAY)# 그레이 스케일로 바꿔야 인식 더 잘함
        # binary_image = model.dotted_line_to_line(prescription)
        table = model.grid_predict(prescription)
        model.extract_element(table)
    except Exception as e:
        print(e)
        continue

#개 1 등 의 단위 요소는 무조건 숫자가 앞에 오는개 맞기 때문에
#re.match(r'(\d+)(.*)') 해서 None이면 반대로 추출해서 순서 바꿔주거나
#re.find_all()로 그냥 숫자만, 문자만 다 골라서 숫자 앞에 문자 뒤에로 매핑 시켜도될거 같음