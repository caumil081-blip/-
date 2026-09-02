# -*- coding: utf-8 -*-
"""기준 파일(사용자 확정 1번 논문)과 대상 파일의 요소별 서식을 비교한다."""
import sys, re, zipfile, collections
sys.path.insert(0, 'hwpx')
import relayout as R

def profile(path):
    z = zipfile.ZipFile(path)
    h = z.read('Contents/header.xml').decode('utf-8')
    d = z.read('Contents/section0.xml').decode('utf-8')
    F = {m.group(1): [f.group(2) for f in re.finditer(r'<hh:font id="(\d+)" face="([^"]*)"', m.group(2))]
         for m in re.finditer(r'<hh:fontface lang="(\w+)" fontCnt="\d+">(.*?)</hh:fontface>', h, re.S)}
    def cf(c):
        m = re.search(r'<hh:charPr id="%s" height="(\d+)"[^>]*>(.*?)</hh:charPr>' % c, h, re.S)
        if not m: return '?'
        b = m.group(2)
        fh = re.search(r'hangul="(\d+)"', b); fl = re.search(r'latin="(\d+)"', b)
        ra = re.search(r'<hh:ratio [^>]*hangul="(\d+)"', b); sp = re.search(r'<hh:spacing [^>]*hangul="(-?\d+)"', b)
        return '%.1fpt %s/%s 장평%s 자간%s' % (int(m.group(1))/100,
            F['HANGUL'][int(fh.group(1))], F['LATIN'][int(fl.group(1))], ra.group(1), sp.group(1))
    def pf(p):
        m = re.search(r'<hh:paraPr id="%s" .*?</hh:paraPr>' % p, h, re.S)
        if not m: return '?'
        s = m.group(0)
        al = re.search(r'horizontal="(\w+)"', s).group(1)
        ls = re.search(r'<hh:lineSpacing type="\w+" value="(\d+)"', s)
        return '%s %s%%' % (al, ls.group(1) if ls else '?')
    RULES = [
        ('한글제목',    lambda t: t.startswith('군 내부 이메일 기반') or t.startswith('AI 기반 계층적')),
        ('영문제목',    lambda t: t.startswith('Design of a Military') or t.startswith('Automating Defense')),
        ('저자명',      lambda t: t.startswith('*, *, *, *, **') or t.startswith('김보라')),
        ('지원기관표기',  lambda t: t.startswith('이 논문은 2026년도')),
        ('요약 제목',    lambda t: t == '요  약'),
        ('요약 본문',    lambda t: t.startswith('군 내부 이메일에는') or t.startswith('국방 정보체계는')),
        ('Abstract제목', lambda t: t == 'Abstract'),
        ('Abstract본문', lambda t: t.startswith('Military organizations') or t.startswith('Defense information')),
        ('Keywords',   lambda t: t.startswith('Keywords')),
        ('장 제목',     lambda t: bool(re.match(r'^[ⅠⅡⅢⅣⅤⅥⅦ]\.', t))),
        ('소제목',      lambda t: bool(re.match(r'^\d+\.\d+ ', t))),
        ('본문',       lambda t: len(t) > 260 and bool(re.match(r'^[가-힣]', t))),
        ('표 캡션',     lambda t: bool(re.match(r'^표 \d+\.', t))),
        ('그림 캡션',    lambda t: bool(re.match(r'^그림 \d+\.', t))),
        ('참고문헌',     lambda t: bool(re.match(r'^\[\d+\]', t))),
    ]
    res = collections.OrderedDict()
    for s, e in R.paragraphs(d):
        para = d[s:e]
        m = re.match(r'<hp:p [^>]*?paraPrIDRef="(\d+)"', para)
        if not m: continue
        t = R.own_text(para).strip()
        own = ''.join(para[a:b] for a, b in R.own_parts(para))
        cids = re.findall(r'charPrIDRef="(\d+)"', own)
        if not cids or not t: continue
        c = collections.Counter(cids).most_common(1)[0][0]
        for name, test in RULES:
            if name not in res and test(t):
                res[name] = (cf(c), pf(m.group(1))); break
    # 표 안 글자
    for m in re.finditer(r'<hp:tbl\b[^>]*>', d):
        s = m.start(); e = d.find('</hp:tbl>', s); blk = d[s:e]
        sz = re.search(r'<hp:sz width="(\d+)"', blk)
        if not sz or int(sz.group(1)) > 30000: continue
        c = re.search(r'charPrIDRef="(\d+)"', blk); p = re.search(r'paraPrIDRef="(\d+)"', blk)
        if c and p: res['표 안 글자'] = (cf(c.group(1)), pf(p.group(1))); break
    return res

if __name__ == '__main__':
    a = profile(sys.argv[1]); b = profile(sys.argv[2])
    print('%-14s %-44s %-44s' % ('요소', '기준(1번 확정본)', '2번'))
    print('-' * 112)
    for k in list(dict.fromkeys(list(a) + list(b))):
        x = a.get(k, ('— 없음', '')); y = b.get(k, ('— 없음', ''))
        mark = '' if x[0] == y[0] else '  ★차이'
        print('%-14s %-44s %-44s%s' % (k, x[0], y[0], mark))
        if x[1] != y[1]: print('%-14s %-44s %-44s  (정렬/줄간격)' % ('', x[1], y[1]))
