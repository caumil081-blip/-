# -*- coding: utf-8 -*-
"""1번 논문 앞머리를 KIIT 공식 양식 규격에 맞춘다(2번과 동일 기준)."""
import re, sys
sys.path.insert(0, 'hwpx')
import relayout as R

H, S = 'hwpx/extracted/Contents/header.xml', 'hwpx/extracted/Contents/section0.xml'
h = open(H, encoding='utf-8').read(); d = open(S, encoding='utf-8').read()
LANGS = ['hangul','latin','hanja','japanese','other','symbol','user']

NEED = ['휴먼명조', 'HCI Poppy', '돋움', '한양견명조', '한양신명조', 'Times New Roman']
TTF  = {'휴먼명조', '돋움', 'Times New Roman', 'HCI Poppy'}

def ensure_fonts():
    """필요한 글꼴이 언어별 목록에 없으면 추가한다(양식과 같은 글꼴을 쓰기 위해)."""
    global h
    added = []
    def fix(m):
        lang, cnt, body = m.group(1), int(m.group(2)), m.group(3)
        have = {f.group(1) for f in re.finditer(r'<hh:font id="\d+" face="([^"]*)"', body)}
        add = ''
        for face in NEED:
            if face in have: continue
            add += ('<hh:font id="%d" face="%s" type="%s" isEmbedded="0">'
                    '<hh:substFont face="한컴바탕" type="TTF" isEmbedded="0" binaryItemIDRef=""/>'
                    '</hh:font>') % (cnt, face, 'TTF' if face in TTF else 'HFT')
            added.append((lang, face)); cnt += 1
        return '<hh:fontface lang="%s" fontCnt="%d">%s%s</hh:fontface>' % (lang, cnt, body, add)
    h = re.sub(r'<hh:fontface lang="(\w+)" fontCnt="(\d+)">(.*?)</hh:fontface>', fix, h, flags=re.S)
    return added


def font_id(lang, face):
    m = re.search(r'<hh:fontface lang="%s" fontCnt="\d+">(.*?)</hh:fontface>' % lang, h, re.S)
    for f in re.finditer(r'<hh:font id="(\d+)" face="([^"]*)"', m.group(1)):
        if f.group(2) == face: return int(f.group(1))
    raise KeyError((lang, face))

def new_char(base, hangul, latin, height, spacing):
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
    """앞머리(문단 20개 이내)에서 조건에 맞는 첫 문단에만 적용."""
    global d
    for k, (s, e) in enumerate(R.paragraphs(d)):
        if k > 20: break
        if not pred(R.own_text(d[s:e]).strip()): continue
        blk = d[s:e]; he = blk.index('>') + 1
        head = re.sub(r'paraPrIDRef="\d+"', 'paraPrIDRef="%d"' % para_id, blk[:he], count=1) if para_id is not None else blk[:he]
        body = re.sub(r'charPrIDRef="\d+"', 'charPrIDRef="%d"' % char_id, blk[he:]) if char_id is not None else blk[he:]
        d = d[:s] + head + body + d[e:]
        return True
    return False

added = ensure_fonts()
print('  글꼴 보강: %d건 %s' % (len(added), sorted({f for _, f in added})))

SPEC = [
    ('한글제목1',  lambda t: t.startswith('군 내부 이메일 기반'),
     ('휴먼명조','HCI Poppy',1700,-7), ('CENTER',130,1000,0)),
    ('한글제목2',  lambda t: t.startswith('산정 시스템 설계'),
     ('휴먼명조','HCI Poppy',1700,-7), ('CENTER',130,0,1000)),
    ('저자명',    lambda t: t == '*, *, *, *, **',
     ('돋움','돋움',1100,5),           ('CENTER',130,1000,1000)),
    ('영문제목1',  lambda t: t.startswith('Design of a Military'),
     ('한양견명조','한양견명조',1500,-7),  ('CENTER',130,1000,0)),
    ('영문제목2',  lambda t: t.startswith('Extraction and Rule-based'),
     ('한양견명조','한양견명조',1500,-7),  ('CENTER',130,0,1000)),
    ('영문저자명', lambda t: t == '*, *, *, *, ***',
     ('휴먼명조','HCI Poppy',1000,5),   ('CENTER',130,700,1000)),
    ('지원기관표기', lambda t: t.startswith('이 논문은 2026년도'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',130,0,0)),
    ('요약문제목',  lambda t: t == '요  약',
     ('돋움','돋움',1050,-6),          ('CENTER',150,0,0)),
    ('요약본문',   lambda t: t.startswith('군 내부 이메일에는'),
     ('휴먼명조','HCI Poppy',920,-6),   ('JUSTIFY',150,0,0)),
    ('영문요약제목', lambda t: t == 'Abstract',
     ('돋움','돋움',1050,-6),          ('CENTER',150,200,0)),
    ('영문요약문',  lambda t: t.startswith('Military organizations'),
     ('한양신명조','Times New Roman',920,-6), ('JUSTIFY',150,0,0)),
    ('Keywords', lambda t: t.startswith('Keywords'),
     ('휴먼명조','Times New Roman',920,-6), ('CENTER',150,0,0)),
]
for name, pred, (kh, kl, sz, sp), (al, ls, pv, nx) in SPEC:
    c = new_char(9, kh, kl, sz, sp)
    p = new_para(15 if al == 'JUSTIFY' else 1, al, ls, pv, nx)
    ok = apply(pred, para_id=p, char_id=c)
    print('  %-10s %-22s %.1fpt 자간%+d  %s %d%%  %s'
          % (name, '%s/%s' % (kh, kl), sz/100, sp, al, ls, '적용' if ok else '★못 찾음'))
open(H, 'w', encoding='utf-8').write(h); open(S, 'w', encoding='utf-8').write(d)
