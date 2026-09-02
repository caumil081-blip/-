# -*- coding: utf-8 -*-
"""두 논문의 '실제 쓰이는' 서식을 논리 요소별로 뽑아 나란히 비교한다."""
import sys, re, zipfile, collections
sys.path.insert(0, 'hwpx')
import relayout as R

def load(path):
    z = zipfile.ZipFile(path)
    return (z.read('Contents/header.xml').decode('utf-8'),
            z.read('Contents/section0.xml').decode('utf-8'))

def fonts(h):
    out = {}
    for m in re.finditer(r'<hh:fontface lang="(\w+)" fontCnt="\d+">(.*?)</hh:fontface>', h, re.S):
        out[m.group(1)] = [f.group(2) for f in re.finditer(r'<hh:font id="(\d+)" face="([^"]*)"', m.group(2))]
    return out

def charfmt(h, F, cid):
    m = re.search(r'<hh:charPr id="%s" height="(\d+)"[^>]*>(.*?)</hh:charPr>' % cid, h, re.S)
    if not m: return '?'
    b = m.group(2)
    fh = re.search(r'hangul="(\d+)"', b); fl = re.search(r'latin="(\d+)"', b)
    ra = re.search(r'<hh:ratio [^>]*hangul="(\d+)"', b)
    sp = re.search(r'<hh:spacing [^>]*hangul="(-?\d+)"', b)
    return '%.1fpt %s/%s 장평%s 자간%s' % (int(m.group(1))/100,
        F['HANGUL'][int(fh.group(1))], F['LATIN'][int(fl.group(1))], ra.group(1), sp.group(1))

def parafmt(h, pid):
    m = re.search(r'<hh:paraPr id="%s" .*?</hh:paraPr>' % pid, h, re.S)
    if not m: return '?'
    s = m.group(0)
    al = re.search(r'horizontal="(\w+)"', s).group(1)
    ls = re.search(r'<hh:lineSpacing type="\w+" value="(\d+)"', s)
    pv = re.search(r'<hc:prev value="(-?\d+)"', s); nx = re.search(r'<hc:next value="(-?\d+)"', s)
    return '%s %s%% 문단위%s 아래%s' % (al, ls.group(1) if ls else '?',
                                    pv.group(1) if pv else '?', nx.group(1) if nx else '?')

def profile(path):
    h, d = load(path); F = fonts(h)
    res = collections.OrderedDict()
    def rec(key, para, cid, pid):
        if key in res: return
        res[key] = (charfmt(h, F, cid), parafmt(h, pid))
    for s, e in R.paragraphs(d):
        para = d[s:e]
        m = re.match(r'<hp:p [^>]*?paraPrIDRef="(\d+)" styleIDRef="(\d+)"', para)
        if not m: continue
        pid = m.group(1)
        t = R.own_text(para).strip()
        own = ''.join(para[a:b] for a, b in R.own_parts(para))
        cids = re.findall(r'charPrIDRef="(\d+)"', own)
        if not cids: continue
        cid = collections.Counter(cids).most_common(1)[0][0]
        if re.match(r'^(표|Table) \d+\.', t):        rec('표 캡션', para, cid, pid)
        elif re.match(r'^(그림|Fig\.) \d+\.', t):    rec('그림 캡션', para, cid, pid)
        elif re.match(r'^[ⅠⅡⅢⅣⅤⅥⅦ]\.', t):        rec('장 제목', para, cid, pid)
        elif re.match(r'^\d+\.\d+ ', t):             rec('소제목', para, cid, pid)
        elif re.match(r'^\[\d+\]', t):               rec('참고문헌', para, cid, pid)
        elif t.startswith('Keywords'):               rec('Keywords', para, cid, pid)
        elif t in ('요  약',):                        rec('요약 제목', para, cid, pid)
        elif t == 'Abstract':                        rec('Abstract 제목', para, cid, pid)
        elif len(t) > 200 and re.search(r'[가-힣]', t[:40]) and '요약' not in res_hint(res):
            pass
    # 본문/표 셀은 따로
    for s, e in R.paragraphs(d):
        para = d[s:e]
        if '<hp:tbl' in para:
            szm = re.search(r'<hp:sz width="(\d+)"', para)
            if not szm or int(szm.group(1)) > 30000:      # 앞머리 1단 상자는 제외
                continue
            for c in re.finditer(r'<hp:tc\b.*?</hp:tc>', para, re.S):
                cid = re.search(r'charPrIDRef="(\d+)"', c.group(0))
                pid = re.search(r'paraPrIDRef="(\d+)"', c.group(0))
                if cid and pid:
                    res.setdefault('표 안 글자', (charfmt(h, F, cid.group(1)), parafmt(h, pid.group(1))))
                    break
            break
    return res

def res_hint(res): return ' '.join(res.keys())

a = profile('hwpx/KIIT_paper1_revised.hwpx')
b = profile('p2/KIIT_paper2_converted.hwpx')
keys = list(dict.fromkeys(list(a) + list(b)))
print('%-12s %-46s %-46s %s' % ('요소', '1번 논문', '2번 논문', ''))
print('-' * 118)
for k in keys:
    x = a.get(k, ('—','—')); y = b.get(k, ('—','—'))
    same = '  일치' if x == y else '  ★차이'
    print('%-12s %-46s %-46s%s' % (k, x[0], y[0], same))
    print('%-12s %-46s %-46s' % ('', x[1], y[1]))
