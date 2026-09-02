# -*- coding: utf-8 -*-
"""표/그림/알고리즘 캡션 '글자 줄'만 가운데 정렬 -> 양쪽 정렬로 바꾼다.
   표·그림을 담고 있는 문단(가운데 정렬이라 표가 가운데에 놓인다)은 건드리지 않는다."""
import re, sys
sys.path.insert(0, '.')
import relayout as R

H, S = 'extracted/Contents/header.xml', 'extracted/Contents/section0.xml'
CAP = re.compile(r'^(표|그림|알고리즘|Table|Fig\.|Algorithm) \d+\.')

h = open(H, encoding='utf-8').read()
cnt = int(re.search(r'<hh:paraProperties itemCnt="(\d+)">', h).group(1))
new_id = cnt
src = re.search(r"<hh:paraPr id=\"1\" .*?</hh:paraPr>", h, re.S).group(0)
clone = (src.replace('<hh:paraPr id="1"', '<hh:paraPr id="%d"' % new_id, 1)
            .replace('<hh:align horizontal="CENTER"', '<hh:align horizontal="JUSTIFY"', 1))
assert 'JUSTIFY' in clone
h = h.replace('<hh:paraProperties itemCnt="%d">' % cnt,
              '<hh:paraProperties itemCnt="%d">' % (cnt + 1), 1)
h = h.replace('</hh:paraProperties>', clone + '</hh:paraProperties>', 1)
open(H, 'w', encoding='utf-8').write(h)

d = open(S, encoding='utf-8').read()
edits, n = [], 0
for s, e in R.paragraphs(d):
    para = d[s:e]
    m = re.match(r'<hp:p [^>]*?paraPrIDRef="1" styleIDRef="6"', para)
    if not m: continue
    if '<hp:tbl' in para or '<hp:pic' in para: continue      # 표/그림 담은 문단 제외
    if not CAP.match(R.own_text(para).strip()): continue     # 캡션 글자 줄만
    head_end = para.index('>') + 1
    head = para[:head_end].replace('paraPrIDRef="1"', 'paraPrIDRef="%d"' % new_id, 1)
    edits.append((s, s + head_end, head)); n += 1
for x, y, rep in sorted(edits, reverse=True):
    d = d[:x] + rep + d[y:]
open(S, 'w', encoding='utf-8').write(d)
print('새 paraPr id=%d(양쪽 정렬) 추가 / 캡션 글자 줄 %d개에만 적용' % (new_id, n))
