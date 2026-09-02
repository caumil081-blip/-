# -*- coding: utf-8 -*-
"""단 폭을 넘는 표를 비율대로 줄이고, 두 논문의 남은 서식 차이를 맞춘다."""
import re, sys

COL = (53858 - 5669*2 - 2268) // 2      # 2단 기준 단 폭 = 20126

def fit_tables(d, limit=30000):
    """표 전체 폭(표 폭 + 바깥 여백)이 단 폭을 넘으면 셀 폭을 비율대로 줄인다.
       limit 보다 큰 표(앞머리 1단 상자)는 건드리지 않는다."""
    out, pos, fixed = [], 0, []
    for m in re.finditer(r'<hp:tbl\b[^>]*>', d):
        s = m.start(); e = d.find('</hp:tbl>', s) + len('</hp:tbl>')
        blk = d[s:e]
        szm = re.search(r'<hp:sz width="(\d+)"', blk)
        om  = re.search(r'<hp:outMargin left="(\d+)" right="(\d+)"', blk)
        if not szm or not om: continue
        cur = int(szm.group(1)); ml, mr = int(om.group(1)), int(om.group(2))
        if cur > limit: continue                       # 본문 표가 아님
        target = COL - ml - mr
        if cur <= target: continue
        f = target / cur
        def scale_row(rm):
            row = rm.group(0)
            ws = [int(x) for x in re.findall(r'<hp:cellSz width="(\d+)"', row)]
            new = [max(1, round(w * f)) for w in ws]
            new[-1] += target - sum(new)               # 반올림 오차를 마지막 칸에서 흡수
            it = iter(new)
            return re.sub(r'(<hp:cellSz width=")\d+', lambda x: x.group(1) + str(next(it)), row)
        nb = re.sub(r'<hp:tr>.*?</hp:tr>', scale_row, blk, flags=re.S)
        nb = re.sub(r'(<hp:sz width=")\d+', r'\g<1>%d' % target, nb, count=1)
        out.append(d[pos:s]); out.append(nb); pos = e
        fixed.append((cur, target))
    out.append(d[pos:])
    return ''.join(out), fixed

def set_para(h, pid, align=None, ls=None, prev=None, nxt=None):
    m = re.search(r'<hh:paraPr id="%d" .*?</hh:paraPr>' % pid, h, re.S)
    if not m: return h, False
    blk = m.group(0); new = blk
    if align: new = re.sub(r'(<hh:align horizontal=")\w+', r'\g<1>%s' % align, new)
    if ls:    new = re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>%d' % ls, new)
    if prev is not None: new = re.sub(r'(<hc:prev value=")-?\d+', r'\g<1>%d' % prev, new)
    if nxt  is not None: new = re.sub(r'(<hc:next value=")-?\d+', r'\g<1>%d' % nxt, new)
    return h.replace(blk, new), new != blk

def set_size(h, cid, height):
    return re.sub(r'(<hh:charPr id="%d" height=")\d+' % cid, r'\g<1>%d' % height, h, count=1)
