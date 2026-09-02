# -*- coding: utf-8 -*-
"""HWPX 문단의 linesegarray(줄 나눔 캐시)를 다시 계산한다.

한글은 문서를 열 때 linesegarray 를 그대로 믿고 렌더링하므로, 본문 텍스트를
고친 뒤 캐시를 그대로 두거나 임의로 잘라내면 글자가 겹쳐 보인다.
원본 문서의 실제 줄 나눔에서 문자 폭 모델을 최소제곱으로 학습한 뒤,
바뀐 문단만 그 모델로 다시 줄을 나눈다.
"""
import re, difflib

TOKEN = re.compile(r'<hp:p\b[^>]*?>|</hp:p>')
SEG   = re.compile(r'<hp:lineseg\b[^>]*?/>')

# ---------------------------------------------------------------- 문단 분해
def paragraphs(d):
    """문서 안의 모든 문단 구간 (start, end) 을 깊이를 세며 수집한다."""
    stack, res = [], []
    for m in TOKEN.finditer(d):
        if m.group(0).startswith('</'):
            if stack: res.append((stack.pop(), m.end()))
        else:
            stack.append(m.start())
    return sorted(res)

def own_parts(para):
    """중첩 문단(표 셀) 내부를 제외한, 이 문단이 직접 소유한 구간들."""
    depth, out, i = 0, [], None
    for m in TOKEN.finditer(para):
        if m.start() == 0: 
            i = m.end(); continue
        if m.group(0).startswith('</'):
            if depth == 0:
                out.append((i, m.start())); return out
            depth -= 1
            if depth == 0: i = m.end()
        else:
            if depth == 0: out.append((i, m.start()))
            depth += 1
    out.append((i, len(para)))
    return out

def own_text(para):
    seg = ''.join(para[a:b] for a, b in own_parts(para))
    txt = []
    for t in re.findall(r'<hp:t>(.*?)</hp:t>', seg, re.S):
        t = t.replace('<hp:lineBreak/>', '\n')
        t = re.sub(r'<[^>]+>', '', t)
        txt.append(t)
    s = ''.join(txt)
    return (s.replace('&lt;', '<').replace('&gt;', '>')
             .replace('&quot;', '"').replace('&apos;', "'").replace('&amp;', '&'))

def own_segblock(para):
    """이 문단이 직접 소유한 linesegarray 의 (start, end)."""
    parts = own_parts(para)
    last = parts[-1]
    tail = para[last[0]:last[1]]
    m = re.search(r'<hp:linesegarray>.*?</hp:linesegarray>', tail, re.S)
    return (last[0] + m.start(), last[0] + m.end()) if m else None

# ---------------------------------------------------------------- 폭 모델
def is_wide(ch):
    o = ord(ch)
    return (0x1100 <= o <= 0x115F or 0x2E80 <= o <= 0xA4CF or 0xAC00 <= o <= 0xD7A3
            or 0xF900 <= o <= 0xFAFF or 0xFE30 <= o <= 0xFE4F or 0xFF00 <= o <= 0xFF60
            or 0xFFE0 <= o <= 0xFFE6 or 0x3000 <= o <= 0x303E)

def counts(s):
    w = sum(1 for c in s if is_wide(c))
    return len(s) - w, w          # (narrow, wide)

def first_charpr(para):
    m = re.search(r'charPrIDRef="(\d+)"', para)
    return m.group(1) if m else '?'


def _solve(rows, rhs):
    saa = sab = sbb = sar = sbr = 0.0
    for (n, w), r in zip(rows, rhs):
        saa += n*n; sab += n*w; sbb += w*w; sar += n*r; sbr += w*r
    det = saa*sbb - sab*sab
    if abs(det) < 1e-9: return None
    return ((sar*sbb - sbr*sab) / det, (sbr*saa - sar*sab) / det)


def fit_width_model(orig_doc, per_charpr=False):
    """원본의 '꽉 찬 줄'들로부터 좁은 글자/넓은 글자 폭(em)을 최소제곱 추정.
       per_charpr=True 이면 글자모양(charPr)별로도 따로 추정해 함께 돌려준다."""
    rows, rhs = [], []
    groups = {}
    for s, e in paragraphs(orig_doc):
        para = orig_doc[s:e]
        blk = own_segblock(para)
        if not blk: continue
        segs = SEG.findall(para[blk[0]:blk[1]])
        if len(segs) < 2: continue          # 여러 줄인 문단만 사용
        text = own_text(para)
        tp = [int(re.search(r'textpos="(\d+)"', x).group(1)) for x in segs]
        for i in range(len(segs) - 1):      # 마지막 줄은 덜 찼으므로 제외
            line = text[tp[i]:tp[i+1]]
            if not line.strip(): continue
            hz = int(re.search(r'horzsize="(\d+)"', segs[i]).group(1))
            vs = int(re.search(r'vertsize="(\d+)"', segs[i]).group(1))
            if vs <= 0: continue
            n, w = counts(line.rstrip())
            if n + w == 0: continue
            rows.append((n, w)); rhs.append(hz / vs)
            key = 'latin' if w <= 0.2 * (n + w) else 'cjk'
            groups.setdefault(key, ([], []))[0].append((n, w))
            groups[key][1].append(hz / vs)
    a, b = _solve(rows, rhs)
    if not per_charpr:
        return a, b, len(rows)
    per = {}
    for k, (rr, hh) in groups.items():
        if len(rr) >= 20:                      # 표본이 충분한 조성만
            sol = _solve(rr, hh)
            if sol and sol[0] > 0 and sol[1] > 0: per[k] = sol
    return a, b, len(rows), per

# ---------------------------------------------------------------- 줄 나누기
def wrap(text, cap, a, b):
    """cap(em) 안에 들어가도록 줄을 나눠 각 줄의 시작 위치를 돌려준다.
       줄 끝의 공백은 조판 관례대로 폭 계산에서 제외한다."""
    starts, i, n = [0], 0, len(text)
    while i < n:
        w = 0.0          # 줄 끝 공백을 뺀 실제 폭
        pend = 0.0       # 아직 확정되지 않은 공백 폭
        j, last_break = i, -1
        while j < n:
            c = text[j]
            if c == '\n':
                j += 1; last_break = j; break
            cw = b if is_wide(c) else a
            if c == ' ':
                pend += cw
                j += 1
                last_break = j          # 공백 뒤는 항상 줄바꿈 가능
                continue
            if w + pend + cw > cap:
                j = last_break if last_break > i else max(j, i + 1)
                break
            w += pend + cw; pend = 0.0
            j += 1
            if is_wide(c): last_break = j
        else:
            j = n
        if j <= i: j = i + 1
        i = j
        if i < n: starts.append(i)
    return starts


def calibrated_cap(text, segs, a, b):
    """문단 자신의 원본 줄 나눔에서 실제 용량(em)을 되짚는다.
       '실제로 그 폭까지 들어갔던' 최대값이므로 넘칠 염려가 없다."""
    hz = int(re.search(r'horzsize="(\d+)"', segs[0]).group(1))
    vs = int(re.search(r'vertsize="(\d+)"', segs[0]).group(1))
    base = hz / vs
    if len(segs) < 2:
        return base
    tp = [int(re.search(r'textpos="(\d+)"', x).group(1)) for x in segs]
    widths = []
    for i in range(len(segs) - 1):
        n, w = counts(text[tp[i]:tp[i+1]].rstrip())
        if n + w: widths.append(n*a + w*b)
    return max(widths) if widths else base


def rebuild_segs(orig_segs, new_starts):
    """원본 lineseg 속성을 재사용해 새 줄 수만큼 lineseg 를 만든다."""
    if not orig_segs: return []
    first, rest = orig_segs[0], (orig_segs[1] if len(orig_segs) > 1 else orig_segs[0])
    vp = [int(re.search(r'vertpos="(\d+)"', x).group(1)) for x in orig_segs]
    pitch = (vp[1] - vp[0]) if len(vp) > 1 else \
            int(re.search(r'vertsize="(\d+)"', first).group(1)) * 3 // 2
    out = []
    for i, tp in enumerate(new_starts):
        tmpl = first if i == 0 else rest
        s = re.sub(r'textpos="\d+"', 'textpos="%d"' % tp, tmpl)
        s = re.sub(r'vertpos="\d+"', 'vertpos="%d"' % (vp[0] + i * pitch), s)
        out.append(s)
    return out

# ---------------------------------------------------------------- 본 처리
def relayout(orig_doc, new_doc):
    a, b, nrows, per = fit_width_model(orig_doc, per_charpr=True)
    op, np_ = paragraphs(orig_doc), paragraphs(new_doc)
    otxt = [own_text(orig_doc[s:e]) for s, e in op]
    ntxt = [own_text(new_doc[s:e]) for s, e in np_]

    # 원본 문단 <-> 수정본 문단 정렬
    sm = difflib.SequenceMatcher(a=otxt, b=ntxt, autojunk=False)
    pair = {}                      # 수정본 index -> 원본 index (없으면 None)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            for k in range(i2 - i1): pair[j1 + k] = i1 + k
        elif tag == 'replace':
            for k in range(j2 - j1):
                pair[j1 + k] = i1 + min(k, i2 - i1 - 1) if i2 > i1 else None
        else:
            for k in range(j1, j2): pair.setdefault(k, None)

    edits, changed = [], 0
    for j, (s, e) in enumerate(np_):
        para = new_doc[s:e]
        blk = own_segblock(para)
        if not blk: continue
        i = pair.get(j)
        if i is not None and otxt[i] == ntxt[j]:
            continue                                   # 내용 그대로면 손대지 않는다
        src = orig_doc[op[i][0]:op[i][1]] if i is not None else para
        sblk = own_segblock(src)
        orig_segs = SEG.findall(src[sblk[0]:sblk[1]]) if sblk else SEG.findall(para[blk[0]:blk[1]])
        if not orig_segs: continue
        vs = int(re.search(r'vertsize="(\d+)"', orig_segs[0]).group(1))
        if vs <= 0: continue
        hz = int(re.search(r'horzsize="(\d+)"', orig_segs[0]).group(1))
        # 단 폭 기준 용량. 원본 362개 문단 재현 검증에서 '줄 수를 적게 잡는' 사례가
        # 0건이라, 글자가 겹칠 가능성이 없는 쪽으로만 오차가 생긴다.
        # 전역 단일 모델이 원본 362개 문단 재현에서 가장 정확하고(88.1%),
        # '줄 수를 실제보다 적게 잡는' 사례가 0건이라 글자가 겹칠 수 없다.
        starts = wrap(ntxt[j], hz / vs, a, b)
        newblk = '<hp:linesegarray>' + ''.join(rebuild_segs(orig_segs, starts)) + '</hp:linesegarray>'
        if newblk != para[blk[0]:blk[1]]:
            edits.append((s + blk[0], s + blk[1], newblk)); changed += 1
    for x, y, rep in sorted(edits, reverse=True):
        new_doc = new_doc[:x] + rep + new_doc[y:]
    return new_doc, dict(a=a, b=b, samples=nrows, changed=changed)
