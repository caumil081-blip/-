# -*- coding: utf-8 -*-
"""문단별 linesegarray(레이아웃 캐시)가 본문 길이와 모순되지 않도록 정리한다.
   중첩 문단(표 셀 안)을 고려해 여는/닫는 태그를 세며 문단 경계를 정확히 잡는다."""
import re, sys

P_OPEN  = re.compile(r'<hp:p\b[^>]*?>')
P_CLOSE = re.compile(r'</hp:p>')
TOKEN   = re.compile(r'<hp:p\b[^>]*?>|</hp:p>')

def spans(d):
    """(start, end) 문단 구간을 깊이를 세며 모두 수집."""
    stack, res = [], []
    for m in TOKEN.finditer(d):
        if m.group(0).startswith('</'):
            if stack: res.append((stack.pop(), m.end()))
        else:
            stack.append(m.start())
    return res

def own_text_len(para):
    """이 문단이 직접 소유한 텍스트 길이. 중첩 문단(표 셀) 내부는 제외."""
    depth, out, i = 0, [], 0
    for m in TOKEN.finditer(para):
        if m.start() == 0:      # 자기 자신의 여는 태그
            continue
        if m.group(0).startswith('</'):
            depth -= 1
            if depth < 0: break
        else:
            if depth == 0: out.append((i, m.start()))
            depth += 1
        if depth == 0 and not m.group(0).startswith('</'):
            pass
        if depth == 0:
            i = m.end()
    out.append((i, len(para)))
    seg = ''.join(para[a:b] for a, b in out)
    return sum(len(re.sub(r'<[^>]+>', '', t)) for t in re.findall(r'<hp:t>(.*?)</hp:t>', seg, re.S))

def own_linesegarray(para):
    """이 문단이 직접 소유한 마지막 linesegarray 의 (start, end)."""
    depth = 0
    for m in TOKEN.finditer(para):
        if m.start() == 0: continue
        if m.group(0).startswith('</'):
            depth -= 1
            if depth < 0:
                tail = para[:m.start()]
                lm = None
                for x in re.finditer(r'<hp:linesegarray>.*?</hp:linesegarray>', tail, re.S):
                    # 깊이 0에 있는 것만
                    lm = x
                return (lm.start(), lm.end()) if lm else None
        else:
            depth += 1
    return None

def normalize(d):
    fixed = 0
    edits = []
    for s, e in spans(d):
        para = d[s:e]
        la = own_linesegarray(para)
        if not la: continue
        # 중첩 문단 내부의 linesegarray 를 잘못 잡았는지 확인: 자기 문단 마지막이어야 한다
        if not para[la[1]:].startswith('</hp:p>'): continue
        tl = own_text_len(para)
        block = para[la[0]:la[1]]
        segs = re.findall(r'<hp:lineseg\b[^>]*?/>', block)
        if not segs: continue
        keep = [x for i, x in enumerate(segs)
                if i == 0 or int(re.search(r'textpos="(\d+)"', x).group(1)) < tl]
        if len(keep) == len(segs): continue
        edits.append((s + la[0], s + la[1],
                      '<hp:linesegarray>' + ''.join(keep) + '</hp:linesegarray>'))
        fixed += 1
    for a, b, rep in sorted(edits, reverse=True):
        d = d[:a] + rep + d[b:]
    return d, fixed

if __name__ == '__main__':
    p = sys.argv[1]
    d = open(p, encoding='utf-8').read()
    d, n = normalize(d)
    open(p, 'w', encoding='utf-8').write(d)
    print('linesegarray 정리한 문단 수: %d' % n)
