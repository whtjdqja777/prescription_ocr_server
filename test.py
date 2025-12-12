import Levenshtein
import re
import pandas as pd

df = pd.read_excel('OpenData_ItemPermit20251127.xls')

name_insurance = df.loc[:, ['품목명', '보험코드']]
name_insurance['보험코드'] = name_insurance['보험코드'].str.split(',').str[0]
name_insurance['품목명'] = name_insurance['품목명'].str.replace(" ","").str.split("(").str[0]
name_insurance.to_csv('name_insurance5.csv', index=False)
