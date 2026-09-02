# -*- coding: utf-8 -*-
"""1번 논문을 기준으로 2번 논문의 남은 서식 차이를 맞추고, 두 논문 모두 표 폭을 단 폭에 맞춘다."""
import re, sys
sys.path.insert(0, 'hwpx')
import relayout as R
from fit_tables import fit_tables, set_para, set_size

# ================================================================ 논문 2
H, S = 'p2/ex/Contents/header.xml', 'p2/ex/Contents/section0.xml'
h = open(H, encoding='utf-8').read(); d = open(S, encoding='utf-8').read()

# (1) 표 안 글자를 1번과 같은 9pt 한양중고딕(charPr 18)으로
n_run = 0
out, pos = [], 0
for m in re.finditer(r'<hp:tbl\b[^>]*>', d):
    s = m.start(); e = d.find('</hp:tbl>', s) + len('</hp:tbl>')
    blk = d[s:e]
    sz = re.search(r'<hp:sz width="(\d+)"', blk)
    if not sz or int(sz.group(1)) > 30000:
        continue
    nb, k = re.subn(r'charPrIDRef="10"', 'charPrIDRef="18"', blk)
    out.append(d[pos:s]); out.append(nb); pos = e; n_run += k
out.append(d[pos:]); d = ''.join(out)
print('논문2 (1) 표 안 글자 %d곳 -> 9pt 한양중고딕 (1번과 동일)' % n_run)

# (2) Keywords 전용 글자모양(9.2pt)을 만들어 적용
cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)">', h).group(1))
kw = cnt
src = re.search(r'<hh:charPr id="10" .*?</hh:charPr>', h, re.S).group(0)
clone = re.sub(r'(<hh:charPr id=")10(" height=")\d+', r'\g<1>%d\g<2>920' % kw, src, count=1)
h = h.replace('<hh:charProperties itemCnt="%d">' % cnt,
              '<hh:charProperties itemCnt="%d">' % (cnt + 1), 1)
h = h.replace('</hh:charProperties>', clone + '</hh:charProperties>', 1)
for s, e in R.paragraphs(d):
    if R.own_text(d[s:e]).strip().startswith('Keywords'):
        d = d[:s] + re.sub(r'charPrIDRef="\d+"', 'charPrIDRef="%d"' % kw, d[s:e]) + d[e:]
        break
print('논문2 (2) Keywords -> 9.2pt (양식 규격, 1번과 동일)')

# (3) 장 제목 정렬을 가운데로 (Ⅰ.서론이 다른 문단모양을 쓰고 있었다)
for pid in (6, 8):
    h, ch = set_para(h, pid, align='CENTER')
print('논문2 (3) 장 제목 문단모양 6·8 -> 가운데 정렬')

# (4) 캡션 문단의 위/아래 여백 제거 (한글 제목과 영문 제목이 벌어지던 원인)
capp = set()
for s, e in R.paragraphs(d):
    t = R.own_text(d[s:e]).strip()
    if re.match(r'^(표|그림|Table|Fig\.) \d+\.', t):
        m = re.match(r'<hp:p [^>]*?paraPrIDRef="(\d+)"', d[s:e])
        if m: capp.add(int(m.group(1)))
for pid in sorted(capp):
    h, _ = set_para(h, pid, prev=0, nxt=0)
print('논문2 (4) 캡션 문단모양 %s -> 문단 위/아래 여백 0' % sorted(capp))

# (5) 표 폭을 단 폭에 맞춤
d, fixed = fit_tables(d)
print('논문2 (5) 표 %d개 폭 축소: %s' % (len(fixed), ['%d->%d' % x for x in fixed]))
open(H, 'w', encoding='utf-8').write(h); open(S, 'w', encoding='utf-8').write(d)

# ================================================================ 논문 1
H1, S1 = 'hwpx/extracted/Contents/header.xml', 'hwpx/extracted/Contents/section0.xml'
h1 = open(H1, encoding='utf-8').read(); d1 = open(S1, encoding='utf-8').read()
# 장 제목 중 Ⅰ.서론만 다른 글자모양(46)을 쓰고 있어 영문 글꼴이 어긋났다
ref13 = re.search(r'<hh:charPr id="13" .*?</hh:charPr>', h1, re.S).group(0)
fr13 = re.search(r'<hh:fontRef [^/]*/>', ref13).group(0)
m46 = re.search(r'<hh:charPr id="46" .*?</hh:charPr>', h1, re.S)
if m46:
    new46 = re.sub(r'<hh:fontRef [^/]*/>', fr13, m46.group(0))
    new46 = re.sub(r'(<hh:charPr id="46" height=")\d+', r'\g<1>1100', new46, count=1)
    h1 = h1.replace(m46.group(0), new46)
    print('논문1 (1) 장 제목 글자모양 46 -> 휴먼고딕/HCI Hollyhock 11pt (13번과 통일)')
h1 = set_size(h1, 38, 1050)      # Abstract 제목 10.6 -> 10.5pt
print('논문1 (2) Abstract 제목 10.6pt -> 10.5pt (양식 규격)')
d1, fixed1 = fit_tables(d1)
print('논문1 (3) 표 %d개 폭 축소: %s' % (len(fixed1), ['%d->%d' % x for x in fixed1]))
open(H1, 'w', encoding='utf-8').write(h1); open(S1, 'w', encoding='utf-8').write(d1)
