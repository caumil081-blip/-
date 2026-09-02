# -*- coding: utf-8 -*-
"""KIIT 공식 양식(논문양식.hwp)에서 읽어낸 서식 규격을 논문에 반영한다.

양식 규격(바이너리 HWP DocInfo/BodyText 파싱으로 확인):
  바탕글(본문)   휴먼명조/Times New Roman 10pt  장평90 자간-6 150% 양쪽
  참고문헌       휴먼명조/Times New Roman 10pt  장평90 자간-6 150% 양쪽 내어쓰기15
  각 장 제목     휴먼고딕/HCI Hollyhock  11pt  장평90 자간-6 150% 가운데
  소제목        한양중고딕              11pt  장평90 자간-6 150% 왼쪽
  그림캡션       한양중고딕               9pt  장평90 자간-6 130% 가운데
  표캡션        한양중고딕               9pt  장평90 자간-6 130% 왼쪽
  요약문제목      돋움                 10.5pt 장평90 자간-6 150% 가운데
  한글제목/영문제목  휴먼명조 / 한양견명조    17/15pt 장평90 자간-7 130% 가운데
  저자명/영문저자명  돋움 / 휴먼명조        11/10pt 장평90 자간+5 130% 가운데
"""
import re, sys
sys.path.insert(0, '.')
import relayout as R

H, S = 'extracted/Contents/header.xml', 'extracted/Contents/section0.xml'
h = open(H, encoding='utf-8').read()
d = open(S, encoding='utf-8').read()

# ---------------------------------------------------------------- 1) 글꼴 추가
NEW_FONT = '한양중고딕'
idx = {}
def add_font(m):
    lang, cnt, body = m.group(1), int(m.group(2)), m.group(3)
    have = {f.group(2): int(f.group(1))
            for f in re.finditer(r'<hh:font id="(\d+)" face="([^"]*)"', body)}
    if NEW_FONT in have:
        idx[lang] = have[NEW_FONT]
        return m.group(0)
    idx[lang] = cnt
    ent = ('<hh:font id="%d" face="%s" type="HFT" isEmbedded="0">'
           '<hh:substFont face="한컴바탕" type="TTF" isEmbedded="0" binaryItemIDRef=""/>'
           '</hh:font>') % (cnt, NEW_FONT)
    return '<hh:fontface lang="%s" fontCnt="%d">%s%s</hh:fontface>' % (lang, cnt + 1, body, ent)
h = re.sub(r'<hh:fontface lang="(\w+)" fontCnt="(\d+)">(.*?)</hh:fontface>', add_font, h, flags=re.S)
print('1) 글꼴 %s 확보 -> 언어별 id %s' % (NEW_FONT, idx))

# ---------------------------------------------------------------- 2) 장평/자간
LANGS = ['hangul', 'latin', 'hanja', 'japanese', 'other', 'symbol', 'user']
SPACING_EXC = {42: -7, 40: -7, 39: 5, 41: 5}     # 제목 -7, 저자명 +5
def fix_char(m):
    cid = int(m.group(1)); blk = m.group(0)
    blk = re.sub(r'<hh:ratio [^/]*/>',
                 '<hh:ratio %s/>' % ' '.join('%s="90"' % l for l in LANGS), blk)
    sp = SPACING_EXC.get(cid, -6)
    blk = re.sub(r'<hh:spacing [^/]*/>',
                 '<hh:spacing %s/>' % ' '.join('%s="%d"' % (l, sp) for l in LANGS), blk)
    return blk
h, n = re.subn(r'<hh:charPr id="(\d+)" .*?</hh:charPr>', fix_char, h, flags=re.S)
print('2) 글자모양 %d개 -> 장평 90%%, 자간 -6 (제목 -7, 저자명 +5)' % n)

# ---------------------------------------------------------------- 3) 글꼴/크기 교정
def set_font(cid, mapping, height=None):
    global h
    m = re.search(r'<hh:charPr id="%d" .*?</hh:charPr>' % cid, h, re.S)
    blk = m.group(0)
    fr = re.search(r'<hh:fontRef ([^/]*)/>', blk).group(1)
    cur = dict(re.findall(r'(\w+)="(\d+)"', fr))
    cur.update({k: str(v) for k, v in mapping.items()})
    blk2 = re.sub(r'<hh:fontRef [^/]*/>',
                  '<hh:fontRef %s/>' % ' '.join('%s="%s"' % (l, cur[l]) for l in LANGS), blk)
    if height:
        blk2 = re.sub(r'(<hh:charPr id="%d" height=")\d+' % cid, r'\g<1>%d' % height, blk2)
    h = h.replace(blk, blk2)

JUNG = {l: idx[l.upper()] for l in LANGS}          # 한양중고딕 (언어별 id)
set_font(14, JUNG)                                  # .CAP 캡션 글자
set_font(37, JUNG)                                  # .H2 소제목
set_font(15, JUNG, height=900)                      # 표 안 글자 10pt -> 9pt
set_font(21, JUNG, height=900)                      # 표 머리글
set_font(13, {'latin': 5})                          # .H1 영문 -> HCI Hollyhock
print('3) 캡션·소제목·표 글자 -> 한양중고딕 / 표 글자 9pt / 장제목 영문 -> HCI Hollyhock')

# ---------------------------------------------------------------- 4) 문단모양
def set_para(pid, align=None, ls=None):
    global h
    m = re.search(r'<hh:paraPr id="%d" .*?</hh:paraPr>' % pid, h, re.S)
    blk = m.group(0); new = blk
    if align: new = re.sub(r'(<hh:align horizontal=")\w+', r'\g<1>%s' % align, new)
    if ls:    new = re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>%d' % ls, new)
    h = h.replace(blk, new)

set_para(30, align='LEFT', ls=130)                  # 표·알고리즘 캡션
set_para(12, align='LEFT')                          # 소제목
# 그림 캡션용 문단모양(가운데 130%)을 새로 추가
cnt = int(re.search(r'<hh:paraProperties itemCnt="(\d+)">', h).group(1))
fig_id = cnt
src = re.search(r'<hh:paraPr id="1" .*?</hh:paraPr>', h, re.S).group(0)
clone = (src.replace('<hh:paraPr id="1"', '<hh:paraPr id="%d"' % fig_id, 1)
            .replace('<hh:lineSpacing type="PERCENT" value="150"',
                     '<hh:lineSpacing type="PERCENT" value="130"', 1))
h = h.replace('<hh:paraProperties itemCnt="%d">' % cnt,
              '<hh:paraProperties itemCnt="%d">' % (cnt + 1), 1)
h = h.replace('</hh:paraProperties>', clone + '</hh:paraProperties>', 1)
print('4) 표·알고리즘 캡션 -> 왼쪽 130%% / 소제목 -> 왼쪽 / 그림 캡션용 paraPr %d(가운데 130%%) 추가' % fig_id)

# 그림 캡션 문단을 새 문단모양으로
FIG = re.compile(r'^(그림|Fig\.) \d+\.')
edits, nfig = [], 0
for s, e in R.paragraphs(d):
    para = d[s:e]
    if not re.match(r'<hp:p [^>]*?paraPrIDRef="1" styleIDRef="6"', para): continue
    if '<hp:tbl' in para or '<hp:pic' in para: continue
    if not FIG.match(R.own_text(para).strip()): continue
    he = para.index('>') + 1
    edits.append((s, s + he, para[:he].replace('paraPrIDRef="1"', 'paraPrIDRef="%d"' % fig_id, 1)))
    nfig += 1
for x, y, rep in sorted(edits, reverse=True):
    d = d[:x] + rep + d[y:]
print('   그림 캡션 %d개 적용' % nfig)

# ---------------------------------------------------------------- 5) 줄 나눔 캐시 전량 삭제
d, nls = re.subn(r'<hp:linesegarray>.*?</hp:linesegarray>', '', d, flags=re.S)
print('5) 서식이 전면 변경되었으므로 줄 나눔 캐시 %d개를 모두 삭제(한글이 다시 조판)' % nls)

open(H, 'w', encoding='utf-8').write(h)
open(S, 'w', encoding='utf-8').write(d)
