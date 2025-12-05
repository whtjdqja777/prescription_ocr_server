import pandas as pd
import Levenshtein
# from runocr import RunOcr
import cv2
import re
#방법1. 동일한 품목명을 찾는다
#방법2. Levenshtein 으로 유사도를 계산하여 임계값 이상의 단어들을 후보군으로 한다


class normalization():
    def __init__(self):

        self.item_name = pd.read_csv('item_name.csv')
        self.item_access_number = pd.read_csv('item_access_number.csv')
        self.name_insurance2 = pd.read_csv('name_insurance3.csv')
        self.drug_unit = ['정','개', 'gm', 'mg', 'mcg','mog','μg','ug' 'ng', 'mL', 'ml','mi' 'L','cc','CC'
                          'IU','회분','포','캡슐','캡슐정','스푼','ml 스푼','g','FTU']
        self.result = ['처 방 전', '(약국제 출용)', '①의료보험 ②의료보호 ③산재보험④자동차보험⑤기타(', ')', '요양기관기호:', '교부연월일및번호', '2016 년10월14일-제00085호', 'ku 10', '명', '칭', '환', '성', 'Q', '전화번호', '7', '멕스번호', '자', '주민등록번호', '090113-4******', '관', 'e-mail주소', '', 'J', '4', '5', '9', '처', '방', '면허종별', '1Y |', '분류', '의료인의', '기호', 'J', '3', '0', '4', '성', '명', '면허번호', '※환자의 요구가있을 때에는 질병분류기호를기제하지 아니합니다', '1일', '1회', '1일', '총', '처방의약품의 명칭', '투여', '부약', '$\\fac}$', '법', '투약량', '부약량', '횟수', '일수', '653800341레보트로시럽', '9', 'cc', '3', 'cc', '3', '3', 
                       '644000941새로딘시럽(로라타딘', '1', '개','33CC' '1', '개', '1', '3', '654100091','유시락스시럽', '18', 'cc', '6', 'cc', '3', '3', 
                       '545700681삼아아토크건조시럽', '안녕하세요', '2', 'gm', '0.6667gm', '3', '3', '642103840','싱카스트추정5밀리그램(몬테루카', '1', '정', '1', '정', '1', '30', '645700564','삼아리도맥스크림', '1', '개', '1', '개', '1', '1', '→1일2회 도포']
        self.set_table = {'insurance_code': [], 'drug_name':[], '1일 투약량':[], '1회 투약량':[],'총 투약 일수':[]}
        self.Dosage = ['투여량', '투약량']
    def find_item_test(self):# 이거 653800341레보트로시럽 마냥 나와서 동일한건 나올수가 없고 일단 저거 분리부터 해야됨
        #그리고 642103840싱카스트추정5밀리그램(몬테루카 이렇게 인식되는것도 있어서 유사도 검사로 매핑하는 함수 만들어야됨
        image = cv2.imread('prescription.jpg', cv2.IMREAD_COLOR)
        
        # result = RunOcr(image)

        print(self.result)
        print(type(self.result))
        for idx in range(len(self.result)):
            
            if len(self.result[idx]) >= 4:
                # inst = self.result[idx].replace(" ", "")
                
                inst = re.sub(r'[^가-힣a-zA-Z0-9]',"", self.result[idx])
                
                match = re.match(r'(\d+)(.*)', inst)

                # print(match)
                if match:#보험코드가 있는 경우 처리
                    # 664582카츄정 처럼 붙어서 나오는 경우 숫자와 문자를 분리하여 처리
                    #붙어서 나오거나 품목명만 있는 경우를 판단 하는 기준이 애매하기 때문에
                    #일단 문자열을 나눠서 match가 not None이면 나눠진 문자열 매핑 실행하고
                    # 품목명만 나온경우는 elif문에서 품목명 유사도로 데이베이스에 품목명과 보험 코드를 찾아 매핑 
                    number, string = match.groups()
                     
                    
                # print('number: ', number)
                # print('string:', string)
                
                   
                    sim_list = [Levenshtein.ratio(i, string) for i in self.name_insurance2['품목명']]
                    max_sim = max(sim_list)
                    if max_sim > 0.7:
                        max_sim_idx_list = []
                        while max_sim in sim_list:
                            
                            max_idx = sim_list.index(max_sim)
                            sim_list = sim_list[max_idx+1:]
                            max_sim_idx_list.append(max_idx)
                        if len(max_sim_idx_list) !=0:
                            for i in max_sim_idx_list:
                                if pd.notna(self.name_insurance2.loc[i, '보험코드']):
                                    insurance_code = self.name_insurance2.loc[i, '보험코드']
                                    break
                        else:
                            insurance_code = number
                            
                        self.set_table['drug_name'].append(string)
                        
                        if pd.notna(insurance_code):
                            insurance_code = insurance_code.split(",")[0]
                            self.set_table['insurance_code'].append(insurance_code)
                        else:
                            self.set_table['insurance_code'].append('(비급여)')
                elif not inst.isdigit():# '64555', '카츄정' 또는 '카츄정' 만나오는 경우 처리
                    sim_list = [Levenshtein.ratio(i, inst) for i in self.name_insurance2['품목명']]
                    max_sim = max(sim_list)
                    
                    if max_sim > 0.7:
                        max_sim_idx_list = []
                        while max_sim in sim_list:
                            
                            max_idx = sim_list.index(max_sim)
                            sim_list = sim_list[max_idx+1:]
                            max_sim_idx_list.append(max_idx)
                        for i in max_sim_idx_list:
                            if pd.notna(self.name_insurance2.loc[i, '보험코드']):
                                insurance_code = self.name_insurance2.loc[i, '보험코드']
                                break
                        self.set_table['drug_name'].append(inst)
                        
                        if pd.notna(insurance_code):
                            insurance_code = insurance_code.split(",")[0]
                            self.set_table['insurance_code'].append(insurance_code)
                        else:
                            self.set_table['insurance_code'].append('(비급여)')
        print(self.set_table)
                    
    def find_item_and_insurance_code(self):
        image = cv2.imread('prescription6.jpg', cv2.IMREAD_COLOR)
        
        result = RunOcr(image)

        print(result)
        print(type(result))
        for idx in range(len(result)):
            
            if len(result[idx]) >= 4:
                inst = result[idx].replace(" ", "").split("(")[0]
                match = re.match(r'(\d+)(.*)', inst)

                # print(match)
                if match:#보험코드가 붙어서 나오는 경우 처리
                    # 664582카츄정 처럼 붙어서 나오는 경우 숫자와 문자를 분리하여 처리
                    #붙어서 나오거나 품목명만 있는 경우를 판단 하는 기준이 애매하기 때문에
                    #일단 문자열을 나눠서 match가 not None이면 나눠진 문자열 매핑 실행하고
                    # 품목명만 나온경우는 elif문에서 품목명 유사도로 데이베이스에 품목명과 보험 코드를 찾아 매핑 
                    number, raw_string = match.groups()
                    string = re.sub(r'[^가-힣a-zA-Z0-9]',"", raw_string)     
                    
                # print('number: ', number)
                # print('string:', string)
                    sim_list = [Levenshtein.ratio(i, string) for i in self.name_insurance2['품목명']]
                    max_sim = max(sim_list)
                    if max_sim > 0.7:
                        self.set_table['drug_name'].append(raw_string)#유사도가 0.7이 넘는게 있으면 원본이름 저장
                        max_sim_idx_list = []
                        #투약량 등 복용법 뽑아 매핑하는 함수
                        self.How_To_Take(result, idx)
                        while max_sim in sim_list:#유사도 리스트에서 가장 큰 유사도들의 인덱스를 뽑아 저장
                            
                            max_idx = sim_list.index(max_sim)
                            sim_list = sim_list[max_idx+1:]
                            max_sim_idx_list.append(max_idx)
                        
                        if len(max_sim_idx_list) !=0:#최대 유사도의 인덱스를 가진 리스트가 비어있지 안다면 수행
                            insurance_code = number
                                
                            pre = 0
                            # print(max_sim_idx_list)
                            for i in max_sim_idx_list: # 최대 유사도 인덱스의 보험 코드와 OCR로 출력한 보험코드의 유사도를 비교하여 가장 비슷한 유사도의 보험코드를 뽑는다
                                print(self.name_insurance2.loc[i,'품목명'], self.name_insurance2.loc[i,'보험코드'])    
                                inst = Levenshtein.ratio(self.name_insurance2.loc[i,'보험코드'], number)
                                if inst > pre:
                                    max_index=i 
                                    pre = inst
                                # print('보험코드 최종선택',self.name_insurance2.loc[max_idx,'품목명'], self.name_insurance2.loc[max_idx,'보험코드'])
                            insurance_code = self.name_insurance2.loc[max_index,'보험코드']#가장 유사한 보험코드 변수에 저장
                            #기존 number와 가장 유사도가 높은 보험코드를 insurance_code 변수에 저장
                        else:#최대 유사도 인덱스 리스트가 비어있으면 해당 품목명의 보험 코드가 데이터셋에 없는 것 임으로 기존 number를 변수에 저장 
                            insurance_code = number

                        if pd.notna(insurance_code):
                            insurance_code = insurance_code.split(",")[0]
                            self.set_table['insurance_code'].append(insurance_code)
                        else:
                            self.set_table['insurance_code'].append('(비급여)')

                elif not inst.isdigit():# ['64555', '카츄정']형태 또는 '카츄정' 만나오는 경우 처리: 보험코드, 품목명이 따로나오거나 보험코드가 없는 경우 처리
                    
                    sim_list = [Levenshtein.ratio(i, inst) for i in self.name_insurance2['품목명']]
                    max_sim = max(sim_list)
                    insurance_code = None
                    if max_sim > 0.7:
                        self.set_table['drug_name'].append(inst)
                        max_sim_idx_list = []
                        while max_sim in sim_list:
                            
                            max_idx = sim_list.index(max_sim)
                            sim_list = sim_list[max_idx+1:]
                            max_sim_idx_list.append(max_idx)
                        
                        if len(max_sim_idx_list) != 0:
                            for i in max_sim_idx_list: #최대 유사도 인덱스 리스트의 값에 해당하는 보험 코드를 뽑는 코드
                                
                                if pd.notna(self.name_insurance2.loc[i, '보험코드']):#해당 품목명 인덱스에 보험코드가 있으면 수행
                                    insurance_code = self.name_insurance2.loc[i, '보험코드']
                                    break
  
                        if pd.notna(insurance_code):#데이터셋에서 추출한 보험 코드가 있으면 수행
                            insurance_code = insurance_code.split(",")[0]#보험코드가 여러개 붙어서 나오는 경우를 처리하는 코드
                            self.set_table['insurance_code'].append(insurance_code)
                        else:# insurance_code가 None이면 보험코드가 없음으로 (알수 없음)으로 처리
                            self.set_table['insurance_code'].append('(알수 없음)')
                    
        print(self.set_table)

    # def How_To_Take(self, result, idx):
        #문자인지 숫자인지 판별하고 문자이면 단위 리스트에 있는지 확인
        #1일 투약량, 1회 투약량, 총 투약일수, 
                
                


            # Levenshtein.ratio()
    def Test(self):
        df1 = pd.read_csv('name_insurance3.csv')
        df2 = pd.read_csv('name_insurance2.csv')

        df1 = pd.concat([df1.loc[:,'품목명'],df2.loc[:,'보험코드']], axis=1)
        df1.to_csv('name_insurance4.csv', index=False)

        
        




        


        
        
#{9, 3} -> 보험코드 최대 최소 길이
#약물명 최대 최소 길이
inst = normalization()
# inst.Test()
inst.find_item()


            