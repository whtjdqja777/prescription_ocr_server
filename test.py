import Levenshtein
Dosage = ['처방의약품의명칭', '1일투약량','1회투약량','1일투여횟수','횟수', '총투약일수','1회투여횟수','1회투여량','투약일수']
t = '총 부약 일수'
t= t.replace(" ", "")
l = [Levenshtein.ratio(t, name ) for name in Dosage]
print(t)
print(l)
print(max(l))
print(len(Dosage))
print(len(l))
print(Levenshtein.ratio(t, '총투약일수'))
