# -*- coding: utf-8 -*-
"""HWP 5.0 BodyText 에서 문단별 (스타일, 문단모양, 글자모양, 본문) 추출."""
import olefile, zlib, struct, sys
from hwpinfo import records, load, ALIGN, LS_TYPE

PARA_HEADER, PARA_TEXT, PARA_CHAR_SHAPE = 0x42, 0x43, 0x44
EXT = {1,2,3,11,12,14,15,16,17,18,21,22,23}   # 8바이트(4WCHAR) 확장 제어문자

def para_text(b):
    out, i = [], 0
    while i + 1 < len(b):
        c = struct.unpack('<H', b[i:i+2])[0]
        if c in EXT: i += 16
        elif c < 32: i += 2
        else: out.append(chr(c)); i += 2
    return ''.join(out)

def paragraphs(path, section=0):
    o = olefile.OleFileIO(path)
    flags = struct.unpack('<I', o.openstream('FileHeader').read()[36:40])[0]
    raw = o.openstream('BodyText/Section%d' % section).read()
    d = zlib.decompress(raw, -15) if flags & 1 else raw
    res, cur = [], None
    for tag, lvl, b in records(d):
        if tag == PARA_HEADER:
            if cur: res.append(cur)
            cur = dict(para=struct.unpack('<H', b[8:10])[0], style=b[10], text='', cs=[])
        elif tag == PARA_TEXT and cur is not None:
            cur['text'] += para_text(b)
        elif tag == PARA_CHAR_SHAPE and cur is not None:
            cur['cs'] = [struct.unpack('<II', b[i:i+8])[1] for i in range(0, len(b), 8)]
    if cur: res.append(cur)
    return res

if __name__ == '__main__':
    info = load('template.hwp')
    han = info['langs']['한글']; lat = info['langs']['영어']
    def fmt(cs, ps):
        c = info['chars'][cs]; p = info['paras'][ps]
        return ('%.1fpt %s/%s 장평%d%% 자간%d %d%s %s' % (
            c['size']/100, han[c['face'][0]] if c['face'][0] < len(han) else '?',
            lat[c['face'][1]] if c['face'][1] < len(lat) else '?',
            c['ratio'][0], c['spacing'][0], p['ls'], LS_TYPE.get(p['ls_type'],''),
            ALIGN.get(p['align'],'?')))
    for sec in (0, 1, 2):
        try: ps = paragraphs('template.hwp', sec)
        except Exception: continue
        print('===== Section%d : 문단 %d개' % (sec, len(ps)))
        for p in ps:
            t = p['text'].strip()
            if not t: continue
            nm = info['styles'][p['style']]['name'] if p['style'] < len(info['styles']) else '?'
            print('  [%-12s] %-58s | %s' % (nm, t[:58], fmt(p['cs'][0] if p['cs'] else 0, p['para'])))
