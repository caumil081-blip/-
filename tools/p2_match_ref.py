# -*- coding: utf-8 -*-
"""2번 논문을 사용자가 확정한 1번 논문 파일의 서식에 맞춘다."""
import re, sys
sys.path.insert(0, 'hwpx')
import relayout as R

H, S = 'p2/ex/Contents/header.xml', 'p2/ex/Contents/section0.xml'
h = open(H, encoding='utf-8').read(); d = open(S, encoding='utf-8').read()
LANGS = ['hangul','latin','hanja','japanese','other','symbol','user']

def font_id(lang, face):
    m = re.search(r'<hh:fontface lang="%s" fontCnt="\d+">(.*?)</hh:fontface>' % lang, h, re.S)
    for f in re.finditer(r'<hh:font id="(\d+)" face="([^"]*)"', m.group(1)):
        if f.group(2) == face: return int(f.group(1))
    raise KeyError((lang, face))

def set_char(cid, hangul=None, latin=None, height=None):
    global h
    m = re.search(r'<hh:charPr id="%d" .*?</hh:charPr>' % cid, re.S and h, re.S)
    blk = m.group(0); new = blk
    if hangul or latin:
        fr = re.search(r'<hh:fontRef ([^/]*)/>', blk).group(1)
        cur = dict(re.findall(r'(\w+)="(\d+)"', fr))
        pick = {'hangul': hangul, 'latin': latin, 'hanja': hangul, 'japanese': hangul,
                'other': latin, 'symbol': latin, 'user': hangul}
        for l in LANGS:
            if pick[l]: cur[l] = str(font_id(l.upper(), pick[l]))
        new = re.sub(r'<hh:fontRef [^/]*/>',
                     '<hh:fontRef %s/>' % ' '.join('%s="%s"' % (l, cur[l]) for l in LANGS), new)
    if height:
        new = re.sub(r'(<hh:charPr id="%d" height=")\d+' % cid, r'\g<1>%d' % height, new, count=1)
    h = h.replace(blk, new)

def clone_char(base, height):
    global h
    cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)">', h).group(1))
    src = re.search(r'<hh:charPr id="%d" .*?</hh:charPr>' % base, h, re.S).group(0)
    cl = re.sub(r'(<hh:charPr id=")%d(" height=")\d+' % base, r'\g<1>%d\g<2>%d' % (cnt, height), src, count=1)
    h = h.replace('<hh:charProperties itemCnt="%d">' % cnt, '<hh:charProperties itemCnt="%d">' % (cnt+1), 1)
    h = h.replace('</hh:charProperties>', cl + '</hh:charProperties>', 1)
    return cnt

def clone_para(base, align, ls, prev, nxt):
    global h
    cnt = int(re.search(r'<hh:paraProperties itemCnt="(\d+)">', h).group(1))
    src = re.search(r'<hh:paraPr id="%d" .*?</hh:paraPr>' % base, h, re.S).group(0)
    cl = re.sub(r'(<hh:paraPr id=")%d' % base, r'\g<1>%d' % cnt, src, count=1)
    cl = re.sub(r'(<hh:align horizontal=")\w+', r'\g<1>%s' % align, cl)
    cl = re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>%d' % ls, cl)
    cl = re.sub(r'(<hc:prev value=")-?\d+', r'\g<1>%d' % prev, cl)
    cl = re.sub(r'(<hc:next value=")-?\d+', r'\g<1>%d' % nxt, cl)
    h = h.replace('<hh:paraProperties itemCnt="%d">' % cnt, '<hh:paraProperties itemCnt="%d">' % (cnt+1), 1)
    h = h.replace('</hh:paraProperties>', cl + '</hh:paraProperties>', 1)
    return cnt

def repoint(pred, para_id=None, char_id=None, once=True):
    global d
    n = 0
    for s, e in R.paragraphs(d):
        if not pred(R.own_text(d[s:e]).strip()): continue
        blk = d[s:e]
        he = blk.index('>') + 1
        head = blk[:he]
        if para_id is not None:
            head = re.sub(r'paraPrIDRef="\d+"', 'paraPrIDRef="%d"' % para_id, head, count=1)
        body = blk[he:]
        if char_id is not None:
            body = re.sub(r'charPrIDRef="\d+"', 'charPrIDRef="%d"' % char_id, body)
        d = d[:s] + head + body + d[e:]
        n += 1
        if once: break
    return n

# (1) 장 제목 영문 글꼴을 기준과 같은 휴먼고딕으로
set_char(17, hangul='휴먼고딕', latin='휴먼고딕')
print('(1) 장 제목 영문 글꼴 -> 휴먼고딕 (기준과 동일)')

# (2) 요약·Abstract 본문을 기준과 같은 10pt 휴먼명조/Times New Roman 으로
set_char(19, hangul='휴먼명조', latin='Times New Roman', height=1000)   # 영문 요약
repoint(lambda t: t.startswith('국방 정보체계는'), char_id=10)             # 한글 요약 -> 본문 글자모양
print('(2) 요약·Abstract 본문 9.2pt -> 10.0pt 휴먼명조/Times New Roman (기준과 동일)')

# (3) Abstract 제목 10.6pt (기준값)
ab = clone_char(20, 1060)
repoint(lambda t: t == 'Abstract', char_id=ab)
print('(3) Abstract 제목 -> 10.6pt (기준값)')

# (4) 앞머리 문단모양을 기준과 동일하게 (제목·저자명은 줄간격이 아니라 문단 여백으로 간격을 준다)
p_kt = clone_para(1, 'CENTER', 70, 1000, 1000)    # 한글제목
p_ka = clone_para(1, 'CENTER', 20, 1000, 1000)    # 한글 저자명
p_et = clone_para(1, 'CENTER', 20, 1000, 1000)    # 영문제목
p_ea = clone_para(1, 'CENTER', 90,  700, 1000)    # 영문 저자명
p_fu = clone_para(1, 'CENTER', 130,   0,    0)    # 지원기관표기
repoint(lambda t: t.startswith('AI 기반 계층적'), para_id=p_kt)
repoint(lambda t: t.startswith('김보라') or t.startswith('*, *, *, *, **'), para_id=p_ka)
repoint(lambda t: t.startswith('Automating Defense'), para_id=p_et)
repoint(lambda t: t.startswith('Bo-Ra Kim') or t.startswith('*, *, *, *, ***'), para_id=p_ea)
print('(4) 제목·저자명 문단모양 신설: 한글제목 70%%, 저자명 20%%, 영문제목 20%%, 영문저자명 90%% (기준값)')

# (5) Keywords 는 기준과 같이 양쪽 정렬
for s, e in R.paragraphs(d):
    if R.own_text(d[s:e]).strip().startswith('Keywords'):
        pid = re.match(r'<hp:p [^>]*?paraPrIDRef="(\d+)"', d[s:e]).group(1)
        blk = re.search(r'<hh:paraPr id="%s" .*?</hh:paraPr>' % pid, h, re.S).group(0)
        h = h.replace(blk, re.sub(r'(<hh:align horizontal=")\w+', r'\g<1>JUSTIFY', blk))
        break
print('(5) Keywords -> 양쪽 정렬 (기준과 동일)')

# (6) 지원기관표기 문단을 앞머리에 추가 (기준 파일과 같은 위치·문구)
FUND = ('이 논문은 2026년도 정부(국방부)의 재원으로 정보통신기획평가원의 지원을 받아 수행된 연구임'
        '(RS-2022-II220601, 군 특화 AI 교육과정 개설·운영(국방 AI개발·운용 과정)(중앙대학교)')
kw = None
for m in re.finditer(r'<hh:charPr id="(\d+)" height="920"', h):
    kw = int(m.group(1))          # 앞서 만든 9.2pt 휴먼명조/Times New Roman
assert kw is not None
anchor = None
for s, e in R.paragraphs(d):
    if R.own_text(d[s:e]).strip() == '요  약':
        anchor = s; break
assert anchor is not None
newp = ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
        '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>') % (p_fu, kw, FUND)
d = d[:anchor] + newp + d[anchor:]
print('(6) 지원기관표기 문단 추가 (요 약 바로 앞, 9.2pt 가운데 130%%)')

open(H, 'w', encoding='utf-8').write(h); open(S, 'w', encoding='utf-8').write(d)
