# -*- coding: utf-8 -*-
"""2번 논문 오타·표기 수정."""
import re, sys
sys.path.insert(0, '.')
import relayout as R
S = 'ex/Contents/section0.xml'
d = open(S, encoding='utf-8').read()

FIX = [
 # 표 2 캡션의 부제가 영문으로 남아 있었다
 ('<hp:t> (same candidate set, best F1)</hp:t>', '<hp:t> (동일 후보 집합, 최고 F1 기준)</hp:t>'),
 # 본문이 표의 옛 영문 열 이름을 가리키고 있었다
 ('표의 edit distance', '표의 편집거리'),
 # 표 2 열 머리글 띄어쓰기 통일
 ('<hp:t>재현율 (전체)</hp:t>', '<hp:t>재현율(전체)</hp:t>'),
 # 5.4절은 균형 표본 정밀도를 0.810 으로 보고한다(0.86 은 F1 값)
 ('정밀도가 0.86에서 0.76으로 떨어지지만', '정밀도가 0.81에서 0.76으로 떨어지지만'),
 # 하이픈 뒤 공백, 쉼표 뒤 공백 누락
 ('(RS- 2022-II220601,군 특화', '(RS-2022-II220601, 군 특화'),
]
for old, new in FIX:
    n = d.count(old)
    assert n == 1, '%r -> %d건' % (old[:45], n)
    d = d.replace(old, new)
    print('  수정: %s' % old.replace('<hp:t>', '').replace('</hp:t>', '')[:56])

# ACKNOWLEDGEMENT 가 '정보' / '통신기획평가원의' 두 문단으로 쪼개져 있었다 -> 한 문단으로
paras = R.paragraphs(d)
hit = None
for k, (s, e) in enumerate(paras):
    if R.own_text(d[s:e]).strip().endswith('재원으로 정보'):
        hit = k; break
assert hit is not None, '쪼개진 감사글 문단을 찾지 못함'
s1, e1 = paras[hit]; s2, e2 = paras[hit + 1]
head = R.own_text(d[s1:e1]).strip()
tail_para = d[s2:e2]
m = re.search(r'<hp:t>(.*?)</hp:t>', tail_para, re.S)
merged = tail_para.replace(m.group(0), '<hp:t>%s%s</hp:t>' % (head, m.group(1)), 1)
d = d[:s1] + merged + d[e2:]
print('  수정: 감사글 문단 병합 ("정보" + "통신기획평가원의…")')

open(S, 'w', encoding='utf-8').write(d)
print('2번 논문 오타 %d건 수정' % (len(FIX) + 1))
