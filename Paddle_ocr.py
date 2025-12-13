
import cv2
from matplotlib import pyplot as plt
import re
from bs4 import BeautifulSoup
import Levenshtein
import pandas as pd
import numpy as np
from paddleocr import PPStructureV3
import html
model = PPStructureV3(lang = 'korean')
class prescription_ocr():
    def __init__(self):
        self.grid_ocr = model
        self.Dosage = ['처방의약품의명칭', '1일투약량','1회투약량','1일투여횟수','횟수', '총투약일수','1회투여횟수','1회투여량','투약일수']
        self.name_insurance = pd.read_csv('name_insurance5.csv')
        self.drug_unit = ['정','개', 'gm', 'mg', 'mcg','mog','μg','ug' 'ng', 'mL', 'ml','mi' 'L','cc','CC',
                          'IU','회분','포','캡슐','캡슐정','스푼','ml 스푼','g','FTU']
        self.table = [['653800341 레보트로시럽', '9 cc', '3 cc', '3', '3'], ['새로딘시럽(로라타딘) 644000941', '개 1', '1 개', '1', '3'], ['유시락스시럽 654100091', '18 cc', '6 cC gm0.6667gm', '3 3', '3 3'], ['싱카스트추정5밀리그램(몬테루카 542103840', '1 정', '정', '1', '30'], ['645700564 삼아리도맥스크림', '개 1', '1 개', '1', '1']]
        self.Dosage_unit = [['횟수', '일수'], ['여량', '약량']]
        self.Usage_division_unit = ['복용','경구투여','투여','도포','외용','점안','점비','점이','흡입','주사','정주','근주','피주','좌약','삽입','질정','설하','사용', '식후']
        #외용도포 같이 공백 기준으로 split이 안되는게 있음으로 도포 in 외용 도포 같은 조건문 추가 필요 
        self.rec_boxes = []
        self.rec_texts = []
        self.Usages_candidate = []
        
        
    def grid_predict(self, img):#격자인식 모델, Beautifulsoup의 html 파서로 행별 요소 출력
        # image = cv2.imread('prescription6.jpg')
        if len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            cv2.imwrite('binary_to_color.png', img)
        img = self.insert_padding(img)
        result = self.grid_ocr.predict(img)

        # print(result)
        result = result[0]
        print(result.keys())
        tables = result.get('table_res_list', [])   
        # print(result)
        # print(type(tables))
        # print(tables)
        
        
        

        if len(tables) >0:
            print('테이블있음')
            print(len(tables))
            for t in tables:

                # print(t['cell_box_list'])
                print('cell_box_list 길이', len(t['cell_box_list']))
                # print('rec_texts 길이', len(t['rec_texts']))
                print('table_ocr_pred', t['table_ocr_pred'])
                t1 = t['table_ocr_pred']

                print('table_ocr_pred-> rec_texts 길이', len(t1['rec_texts']))
                self.rec_texts = t1['rec_texts']
                self.rec_boxes = t1['rec_boxes']

                for i in range(len(t1['rec_boxes'])):

                    print('rec_texts : rec_boxes', t1['rec_texts'][i], t1['rec_boxes'][i],': x_min, y_min, x_max, y_max')
                    #보니까  y_min기준으로 정렬을 하든 총합 기준으로 정렬을 하고 x기준으로 행 나눠주면 될거 같기도
                # print(t['table_region_id'])
                html = t['pred_html']       # 표 전체 HTML
            print(type(html))
            print(html)
            soup = BeautifulSoup(html,'html.parser')

            table = []
            for tr in soup.find_all('tr'):
                row =[]
                for td in tr.find_all(['td','th']):
                    row.append(td.get_text(strip = True))
                    #모든 용법 <td> </td>가 같은 row에 있는 drug_info 리스트에 같이 들어감 -> 용법에 대한 <td></td>를 분리하는 코드 짜야됨
                    #용법이라는 단어가 잘 인식이 안됨 -> 용법은 고정이니까 그냥 Dosage리스트에 용법 추가 
                    #용법 써있는게 재각각임, 1. 특정 약물에 대해서만 써 있는경우, 2. 모든 약물에 대해서 써있는 경우, 3. 그냥 약물에 상관없이 써있는 경우, 4. 안써있는 경우
                    #1번의 경우 지금 로직이 tr 기준으로 같은 row에 있는 대에 용법을 통으로 같이 넣어버리기 때문에 1번째 용법은 해당 row의 약물에 대한 용법이 맞음
                    #다음에 오는 용법이 어느 약물에 해당하는 용법인지를 모름
                    #좌표 기준 방법: 약물명이나 보험코드가 인식된 y좌표에 해당 하는 모든 좌표 박스(rec_boxs) 가져옴
                if row:
                    table.append(row)
            print(table)
            Usage_collection = soup.find_all('td', rowspan = True)
            print('Whole_Usage_collection', Usage_collection[0].get_text(strip = True))

            for td in Usage_collection:
                print('Several_Usage_collection', td.get_text(strip=True))
                element = td.get_text(strip=True).split(" ")
                print('element: ', element)
                usage_inst = [] 
                cond = True
                for w in element:
                    usage_inst.append(w)
                    if any(i in w for i in self.Usage_division_unit):
                        self.Usages_candidate.append(" ".join(usage_inst))
                        usage_inst = []

            print('Usage_candidate', self.Usages_candidate)
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
                if any(np.array(Dosratiolist) > 0.7):# Dosage 하고 비교한 값이 0.7이 넘으면 실행
                    print(Dosratiolist)
                    maxratio = max(Dosratiolist)
                    maxratio_idx = Dosratiolist.index(maxratio)            
                    return_Dosage.append(self.Dosage[maxratio_idx])
                
                elif leninst>=2:
                    
                    
                    if  re.match(r'(\d{5,})\s*(.+)', inst.replace(" ","")):
                        print('1번쩨')
                        
                        d, s = re.match(r'(\d{5,})\s*(.+)', inst.replace(" ","").split('(')[0]).groups()
                        print(d, s)
                        name_ratio_max = 0
                        insurance_ratio_max = False
                            
                        if float(d) in self.name_insurance['보험코드'].values:
                            insurance_ratio_max = True
                            
                        else:
                            name_ratio = [Levenshtein.ratio(i, s) for i in self.name_insurance['품목명']]
                            name_ratio_max = max(name_ratio)


                        if insurance_ratio_max:
                            name = self.name_insurance.loc[self.name_insurance['보험코드'] == float(d), '품목명'].iloc[0]

                        elif name_ratio_max > 0.7:
                            idx = name_ratio.index(name_ratio_max)
                            name = self.name_insurance.loc[idx, '품목명']
                            print('else_name', name)
                        # 여기서 부터 용법 찾는 코드 -> 이거 따로 함수화 해야함 ->  if re.match(r'(\d{5,})\s*(.+)', inst) elif ... 으로 사용할 정규식 정해주고 돌리면 될듯  
                        #함수로 만들어서 1번째, 2번째, 3번째 메인코드에 붙이기

                        if name:
                            usage = self.Find_Usage(name, 1)#여기서 
                            find_name_idx = box.index(inst)
                            if len(box) > len(return_Dosage):# 이거 검토한번 필요  -> Find_usage가 문제인줄알았는데 저함수에서 마지막요소 뽑아다 추가 안헀는데듀 I 1같은 마지막요소가 추가되어있음
                                drug_info = box[find_name_idx+1:len(return_Dosage)-1]# 품목명을 제외한 return_Dosage 길이만큼의 요소를 뽑아야되서 이렇게 했는데 여전히 [find_name_idx+1:]한거 마냥 찍힘
                            else:
                                drug_info = box[find_name_idx+1:]
                            if usage:
                                drug_info.append(usage)
                            drug_info.insert(0,name)
                            print('추가될 drug_info', drug_info)
                            return_drug_info.append(drug_info)
                            print('추가된 return_drug_info', return_drug_info)

                    elif re.match(r'^(.+?)(\d{5,})$', inst.replace(" ","")):
                        print('2번쩨')
                        
                        #싱카스트츄정5밀리그램 이거 싱카스트츄정까지만 짤라서 유사도 0.6666으로 나옴
                        #이부분 고치기
                        #러프한 방법: 대부분 보험코드하고 품목명 사이에 공백이 있기 때문에 공백을 기준으로 나눈다
                        match = re.match(r'^(.+?)(\d+)$', inst.replace(" ",""))
                        
                        
                        string, number = match.groups()
                         
                        string = string.split('(')[0].replace(" ","")
                        nameratio = [Levenshtein.ratio(name, string) for name in self.name_insurance.loc[:, '품목명']]
                        max_name_ratio = max(nameratio)
                        name_in_dataset_idx = nameratio.index(max_name_ratio)
                        print(string, max_name_ratio)
                        if max_name_ratio > 0.7:
                            print('통과', string, max_name_ratio)
                            drug_info = []
                            
                            # name = self.name_insurance.loc[nameratio.index(max_name_ratio), '품목명']
                            usage = self.Find_Usage(name, 2)
                            find_name_idx = box.index(inst)
                            if len(box) > len(return_Dosage):
                                drug_info = box[find_name_idx+1:len(return_Dosage)-1]
                            else:
                                drug_info = box[find_name_idx+1:]
                            print('추가전 drug_info', drug_info)
                            if usage:
                                drug_info.append(usage)
                            drug_info.insert(0,self.name_insurance.loc[name_in_dataset_idx, '품목명'])
                            print('추가될 drug_info', drug_info)
                            return_drug_info.append(drug_info)
                            print('추가된 return_drug_info', return_drug_info)

                    else:
                        print('3번쩨')
                    
                        if not inst.isdigit():
                            col = '품목명'
                            cond = 0.7
                            inst = inst.split('(')[0].replace(" ","")
                        else:
                            col = '보험코드'
                            cond = 0.85
                            

                        
                        
                        nameratio = [Levenshtein.ratio(str(i).split(".")[0], inst) if pd.notna(i) else 0 for i in self.name_insurance.loc[:, col] ]# 이거 Levenshtein이 내부적으로 len 사용하기때문에 int, float 형은 str변환해줘야됨
                        max_name_ratio = max(nameratio)
                        name_in_dataset_idx = nameratio.index(max_name_ratio)
                        print(inst, max_name_ratio)
                        
                        if max_name_ratio > cond:
                            print('통과', inst, max_name_ratio)
                            drug_info = []
                            
                            name = self.name_insurance.loc[name_in_dataset_idx, '품목명']
                            
                            if  all(name not in i for i in return_drug_info): 
                                usage = self.Find_Usage(name, None)
                                find_name_idx = box.index(inst)
                                if len(box) > len(return_Dosage):
                                    drug_info = box[find_name_idx+1:len(return_Dosage)-1]
                                else:
                                    drug_info = box[find_name_idx+1:]

                                if usage:
                                    drug_info.append(usage)
                                drug_info.insert(0,self.name_insurance.loc[name_in_dataset_idx, '품목명'])
                                print('추가될 drug_info', drug_info)
                                return_drug_info.append(drug_info)
                                print('추가된 return_drug_info', return_drug_info)
                    
                
        return_Dosage.append('용법')
        return_drug_info = [i[:len(return_Dosage)-1]+[i[-1]] for i in return_drug_info]# 여기서 [i[-1]] 추가하는 것 때문에 용법이 없는 애들도 ''가 추가 되는데 이게 
                                                                                        # 대부분의 경우 해당 셀이 비어 있어서 ''로 출려되는 거기 때문에 나중에 후처리하던지 그냥 쓰면 될듯
        print(return_drug_info)
        print(return_Dosage)
        #여기서 오류 발생 return_drug_info이 [None, None, None, None]으로 나옴
        for i in range(len(return_drug_info)):#순서 잘못된거 고치는 코드 + 인식 잘못된 애들 바꾸거나 수정
            for j in range(1, len(return_drug_info[i])):
                if re.match(r'(.+?)(\d+\.?\d*)$', return_drug_info[i][j].replace(" ","")):# 이건 '개 1' 이렇게 나오는거 고쳐주는 코드 약물쪽에서 문자가 앞에 나오는 경우는 없다고 가정하고 '1개'와 같이 고쳐줌 
                    print("조건 포인트:", return_drug_info[i][j])
                    match = re.match(r'(.+?)(\d+\.?\d*)$', return_drug_info[i][j].replace(" ",""))
                    s, t = match.groups()
                    print('1')
                    if s in self.drug_unit:
                        
                        return_drug_info[i][j] = t+s
                if return_Dosage[j][-2:] in self.Dosage_unit[0] and not return_drug_info[i][j].isdigit():#횟수, 일수에 포함이 되는 애인데 숫자가 아니면
                    return_drug_info[i][j] = ''.join(re.findall('\d', return_drug_info[i][j]))
                elif return_Dosage[j][-2:] in self.Dosage_unit[1]:
                    m = re.match(r'(\d+\.?\d*)(.*)', return_drug_info[i][j].replace(" ",""))
                    
                    if m: 
                        int1, unit = m.groups()
                        if all(np.array(self.drug_unit) != unit): #약물단위 리스트에 매칭되는게 하나도 없으면 유사도 계산해서 매칭 시켜줌
                            unit_sims = [Levenshtein.ratio(unit, i) for i in self.drug_unit]
                            max_ratio_unit = max(unit_sims)
                            max_unit = self.drug_unit[unit_sims.index(max_ratio_unit)]
                            return_drug_info[i][j] = int1+max_unit

                        
                #if 여기에 I 1  같이 잘못 인식된 넘들 있으면 I같은거 제거해주는 코드 만들어야됨 -> re.find_all은 OO정5밀리 이런거 나오면 5만 남기고 없에서 안돼고 
                    #이름 다음: j가 1이상 일때 요소들을 숫자와 문자로 분리해서 문자가 drug_unit에 없으면 없에기 분리 방법은  re.match로 앞에 숫자 1개 이상 뒤에 문자 1개이상, 앞에 문자 1개이상 뒤에 숫자 1개 이상으로 하는게 좋을듯
                    #1회 투약량, 1일 투약량, 1회 투여량, 1일 투여량 등 -> 약물 단위(정, gm, cc 등)이 있어야하고
                    #1일 투여횟수, 총 투약 일수, 투약 일수 등 -> 단위가 없음
                    # 투여량, 투약량 -> 단위 있음
                    # 횟수, 일수 -> 단위 없음
                    # 뒤에서 2개 (여량, 약량),(횟수, 일수)이들이 이미 Dosage에서 매핑 되서 나온거기 때문에 유사도 검사는 필요없고
                    # 뒤에서 2개 슬라이싱 해서 [여량, 약량], [횟수, 일수] 두 리스트 중 어디에 포함되는지 확인하고 단위를 붙일지 말지를 결정 \
                    # 이 문제는 로직 내부에 코드 추가하여 해결함
                
                            
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
    def Find_Usage(self, name, autho):#1번 문제(모든약물에 대해 용법이 써있는 경우), 2번 문제(특정약물에 대해 용법이 써있는 경우)에 대해 용법을 추출 하는 함수
                                    #3번 문제(모든약물에 대해 공통 용법이 써있는 경우) -> 이건 찾아보니까 케이스가 없음 나중에 생기면 코드 새로 넣기
                                    #문제: '1일 1회 도포' 이거 ['1일', '1회', '도포']각각 다른 셀로 분류되는 케이스가 있음
                                    
                                    #해결 아이디어1: Dosage의 마지막쪽 요소들은 투약 횟수, 투약 일수 등으로 숫자로만 이루어진 요소임
                                    #뒤에서 부터 돌면서 처음으로 만나는 숫자요소 뒤에 애들의 좌표를 묶어 용법으로 사용한다
                                    #해당 아이디어 문제점: 이 함수가 품목명 찾는 코드 돌면서 같이 실행되고 있어서 이상 문자 제거하는 후처리 로직을 수행하지 않고 용법을 추가하기 때문에
                                    #마지막 요소 (횟수, 일수)가 후처리되지 않고 I1 마냥 나오면 숫자 요소를 찾지 못하거나 I1을 비롯한 앞의 요소들을 포함하여 용법에 들어갈 수 있다.
                                    #또한, 에초에 해당 Dosage가 인식이 안된경우도 고려 (복용량, 투약량)등만 있는 경우 self.Dosage_unit으로 유사도 비교하던지 해서 해결 필요
                                    # 해결방법: 해당 후처리 로직을 품목명 찾는 과정에서 수행하던지 용법 추가를 해당 후처리 후 수행하던지 해야됨 

                                    #해결 아이디어2: rec_boxes, rec_texts 보면 [-> 1일 1회 도포] 이게 공백을 기준으로 나뉘어져 각각의 셀로 인식하고 있는것을 볼 수 있음
                                    #그럼 html_pred에 있는 <td 'rowspan'=6> -> 1일 1회 도포 -> 1일 2회 도포...</td>를 볼수 있는데 
                                    #[도포, 복용, 분, 식후]등의 대표적인 용법 구분 리스트를 만들어 해당 텍스트를 split(" ")으로 각각의 용법으로 나누고
                                    # 용법구분리스트가 해당 리스트를 돌면서 유사도 비교를 통해 나온 값이 임계값 이상이면 해당 요소(ex)도포)를 기준으로 앞에 있는 애들을 +로 붙이고 슬라이싱으로 해당 요소 앞의 요소들은 지워준다
                                    # 이를 공백 리스트가 될때 까지 반복한다.
                                    #이후 품목명이 있는 셀의 y값을 기준으로 셀들을 모아 마지막 셀부터 돌면서 해당 셀의 요소가 용법 구분 리스트에 있는거면 해당 요소의 위치 부터
                                    # 맨 앞까지 돌면서 요소들을 붙이고 ['1일1회도포', '1일2회도포'](위에서 추출한 용법을 공백 제거한 리스트)들과 비교하면서 같아지면
                                    # 해당 drug_info리스트에 해당 용법 추가 
                                    #문제: 처방정 용법 부분이 격자로 되어 있는 경우 격자로 인식되어 <td rowspan = "5"> 이런식으로 나오지 않을 수 있음 이 경우는 <td rowspan>을 찾는 과정에서 없으면 위의 용법 찾을 필요가 없기때문에
                                    #용법인 해당 행의 마지막 요소를 용법으로 쓰면 됨 -> ''같은게 들어 있을 경우는 페스하면 되고 용법구분리스트에 포함이 안된에도 일단 페스
        if autho == 1:               
            cond = r'(\d{5,})\s*(.+)'
        elif autho == 2:
            cond = r'^(.+?)(\d{3,})$'
        else:
            cond = None

        if cond:
            usage_ratio_list = [Levenshtein.ratio(re.match(cond,  i.replace(" ","").split('(')[0]).group(2), name)  if re.match(cond,  i.replace(" ","").split('(')[0]) else Levenshtein.ratio(i, name) for i in self.rec_texts ]
                        # for i,j in zip(max_usage_ratio, )
        else:
            usage_ratio_list = [Levenshtein.ratio(i, name) for i in self.rec_texts ]
        print('usage_ratio_list',usage_ratio_list)
        max_usage_ratio = max(usage_ratio_list)
        print('max_usage_ratio',max_usage_ratio)
        last_element = None
        if max_usage_ratio > 0.8:#이거 ratio
            max_usage_idx = usage_ratio_list.index(max_usage_ratio)
            name_min_y = self.rec_boxes[max_usage_idx][1]
            upper_name_min_y = name_min_y + 20
            lower_name_min_y = name_min_y - 20
            same_row_list = [(self.rec_boxes[i][0], self.rec_texts[i]) for i in range(len(self.rec_boxes)) if lower_name_min_y <= int(self.rec_boxes[i][1]) <= upper_name_min_y]
            same_row_list.sort(key= lambda x: x[0])
            print('extract_element First: row_list',same_row_list)
            print('extract_element First: last of row_list', same_row_list[-1])
            if same_row_list[-1][-1]: 
                
                last_element = same_row_list[-1][-1]
            
            
        if last_element and not last_element.replace(" ","").isdigit():
            return last_element
        else:
            return None
        
        
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