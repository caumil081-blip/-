# -*- coding: utf-8 -*-
"""1번 논문 오타 수정."""
import re
S = 'extracted/Contents/section0.xml'
d = open(S, encoding='utf-8').read()
FIX = [
 # 앞머리 각주: 여는 괄호 '연구임(' 이 닫히지 않았다
 ('연구임(RS-2022-II220601, 군 특화 AI 교육과정 개설·운영(국방 AI개발·운용 과정)(중앙대학교)',
  '연구임(RS-2022-II220601, 군 특화 AI 교육과정 개설·운영(국방 AI 개발·운용 과정)(중앙대학교))'),
 # ACKNOWLEDGEMENT: 하이픈 뒤 공백, 쉼표 뒤 공백 누락
 ('(RS- 2022-II220601,군 특화', '(RS-2022-II220601, 군 특화'),
]
for old, new in FIX:
    n = d.count(old)
    assert n == 1, '%r -> %d건' % (old[:40], n)
    d = d.replace(old, new)
    print('  수정: %s' % old[:56])
open(S, 'w', encoding='utf-8').write(d)
print('1번 논문 오타 %d건 수정' % len(FIX))
