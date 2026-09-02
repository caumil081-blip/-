# -*- coding: utf-8 -*-
"""앞머리(제목·저자명·지원기관표기·요약)를 KIIT 공식 양식 규격에 맞춘다.

양식(논문양식.hwp) 본문에서 읽어낸 실제 값:
  한글제목      휴먼명조/HCI Poppy  17.0pt 장평90 자간-7  가운데 130% 문단위10 아래10
  영문제목      한양견명조           15.0pt 장평90 자간-7  가운데 130% 문단위10 아래10
  저자명       돋움               11.0pt 장평90 자간+5  가운데 130% 문단위10 아래10
  영문저자명     휴먼명조/HCI Poppy  10.0pt 장평90 자간+5  가운데 130% 문단위10 아래10
  지원기관표기    휴먼명조/Times New Roman 9.2pt 자간-6   가운데 130%
  요약문제목     돋움              10.5pt              가운데 150%
  요약본문      휴먼명조/HCI Poppy   9.2pt              양쪽  150%
  영문요약문     한양신명조/Times New Roman 9.2pt         양쪽  150%
  key words   휴먼명조/Times New Roman 9.2pt           가운데 150%
"""
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

def new_char(base, hangul, latin, height, spacing):
    """base 를 복제해 글꼴·크기·자간을 지정한 새 글자모양을 만든다."""
    global h
    cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)">', h).group(1))
    src = re.search(r'<hh:charPr id="%d" .*?</hh:charPr>' % base, h, re.S).group(0)
    cl = re.sub(r'(<hh:charPr id=")%d(" height=")\d+' % base, r'\g<1>%d\g<2>%d' % (cnt, height), src, count=1)
    pick = {'hangul': hangul, 'latin': latin, 'hanja': hangul, 'japanese': hangul,
            'other': latin, 'symbol': latin, 'user': hangul}
    cl = re.sub(r'<hh:fontRef [^/]*/>',
                '<hh:fontRef %s/>' % ' '.join('%s="%d"' % (l, font_id(l.upper(), pick[l])) for l in LANGS), cl)
    cl = re.sub(r'<hh:ratio [^/]*/>', '<hh:ratio %s/>' % ' '.join('%s="90"' % l for l in LANGS), cl)
    cl = re.sub(r'<hh:spacing [^/]*/>',
                '<hh:spacing %s/>' % ' '.join('%s="%d"' % (l, spacing) for l in LANGS), cl)
    h = h.replace('<hh:charProperties itemCnt="%d">' % cnt, '<hh:charProperties itemCnt="%d">' % (cnt+1), 1)
    h = h.replace('</hh:charProperties>', cl + '</hh:charProperties>', 1)
    return cnt

def new_para(base, align, ls, prev, nxt):
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

def apply(pred, para_id=None, char_id=None):
    global d
    for s, e in R.paragraphs(d):
        if not pred(R.own_text(d[s:e]).strip()): continue
        blk = d[s:e]; he = blk.index('>') + 1
        head = blk[:he]; body = blk[he:]
        if para_id is not None:
            head = re.sub(r'paraPrIDRef="\d+"', 'paraPrIDRef="%d"' % para_id, head, count=1)
        if char_id is not None:
            body = re.sub(r'charPrIDRef="\d+"', 'charPrIDRef="%d"' % char_id, body)
        d = d[:s] + head + body + d[e:]
        return True
    return False

SPEC = [
    ('한글제목',   lambda t: t.startswith('AI 기반 계층적'),
     ('휴먼명조','HCI Poppy',1700,-7), ('CENTER',130,1000,1000)),
    ('저자명',     lambda t: t.startswith('김보라'),
     ('돋움','돋움',1100,5),           ('CENTER',130,1000,1000)),
    ('한글소속',   lambda t: t.startswith('1) 국방부'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',130,0,0)),
    ('영문제목',   lambda t: t.startswith('Automating Defense'),
     ('한양견명조','한양견명조',1500,-7),  ('CENTER',130,1000,1000)),
    ('영문저자명', lambda t: t.startswith('Bo-Ra Kim'),
     ('휴먼명조','HCI Poppy',1000,5),   ('CENTER',130,700,1000)),
    ('영문소속1',  lambda t: t.startswith('1) Ministry'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',130,0,0)),
    ('영문소속2',  lambda t: t.startswith('2) Department'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',130,0,0)),
    ('영문소속3',  lambda t: t.startswith('3) Defense AI'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',130,0,0)),
    ('요약문제목', lambda t: t == '요  약',
     ('돋움','돋움',1050,-6),          ('CENTER',150,0,0)),
    ('요약본문',   lambda t: t.startswith('국방 정보체계는'),
     ('휴먼명조','HCI Poppy',920,-6),   ('JUSTIFY',150,0,0)),
    ('영문요약제목', lambda t: t == 'Abstract',
     ('돋움','돋움',1050,-6),          ('CENTER',150,200,0)),
    ('영문요약문', lambda t: t.startswith('Defense information'),
     ('한양신명조','Times New Roman',920,-6), ('JUSTIFY',150,0,0)),
    ('Keywords',  lambda t: t.startswith('Keywords'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',150,0,0)),
]
for name, pred, (kh, kl, sz, sp), (al, ls, pv, nx) in SPEC:
    c = new_char(10, kh, kl, sz, sp)
    p = new_para(7 if al == 'JUSTIFY' else 1, al, ls, pv, nx)
    ok = apply(pred, para_id=p, char_id=c)
    print('  %-10s %-22s %.1fpt 자간%+d  %s %d%% 위%d 아래%d  %s'
          % (name, '%s/%s' % (kh, kl), sz/100, sp, al, ls, pv, nx, '적용' if ok else '해당 없음'))

# 지원기관표기 문단 추가 (양식 위치: 저자 정보 다음, 요 약 앞)
FUND = ('이 논문은 2026년도 정부(국방부)의 재원으로 정보통신기획평가원의 지원을 받아 수행된 연구임'
        '(RS-2022-II220601, 군 특화 AI 교육과정 개설·운영(국방 AI개발·운용 과정)(중앙대학교)')
if '이 논문은 2026년도 정부(국방부)의 재원으로 정보통신기획평가원의 지원을 받아 수행된 연구임(RS' not in d:
    c = new_char(10, '휴먼명조', 'Times New Roman', 920, -6)
    p = new_para(1, 'CENTER', 130, 0, 0)
    anchor = next(s for s, e in R.paragraphs(d) if R.own_text(d[s:e]).strip() == '요  약')
    d = d[:anchor] + ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
                      '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>' % (p, c, FUND)) + d[anchor:]
    print('  %-10s 9.2pt 휴먼명조/Times New Roman  CENTER 130%%  추가' % '지원기관표기')

open(H, 'w', encoding='utf-8').write(h); open(S, 'w', encoding='utf-8').write(d)
