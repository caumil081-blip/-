# -*- coding: utf-8 -*-
"""HWP 5.0 바이너리(DocInfo)에서 스타일별 글꼴/크기/장평/자간/줄간격/정렬을 뽑는다."""
import olefile, zlib, struct, sys

TAG = dict(ID_MAPPINGS=0x11, FACE_NAME=0x13, CHAR_SHAPE=0x15, PARA_SHAPE=0x19, STYLE=0x1A)
ALIGN = {0:'양쪽', 1:'왼쪽', 2:'오른쪽', 3:'가운데', 4:'배분', 5:'나눔'}
LS_TYPE = {0:'%', 1:'고정', 2:'여백만', 3:'최소'}

def records(buf):
    i = 0
    while i + 4 <= len(buf):
        v = struct.unpack('<I', buf[i:i+4])[0]; i += 4
        tag, level, size = v & 0x3FF, (v >> 10) & 0x3FF, (v >> 20) & 0xFFF
        if size == 0xFFF:
            size = struct.unpack('<I', buf[i:i+4])[0]; i += 4
        yield tag, level, buf[i:i+size]
        i += size

def wstr(b, p):
    n = struct.unpack('<H', b[p:p+2])[0]; p += 2
    return b[p:p+n*2].decode('utf-16-le'), p + n*2

def load(path):
    o = olefile.OleFileIO(path)
    flags = struct.unpack('<I', o.openstream('FileHeader').read()[36:40])[0]
    raw = o.openstream('DocInfo').read()
    d = zlib.decompress(raw, -15) if flags & 1 else raw
    fonts, chars, paras, styles, mapping = [], [], [], [], None
    for tag, lvl, b in records(d):
        if tag == TAG['ID_MAPPINGS']:
            mapping = list(struct.unpack('<%dI' % (len(b)//4), b))
        elif tag == TAG['FACE_NAME']:
            prop = b[0]; name, p = wstr(b, 1)
            fonts.append(name)
        elif tag == TAG['CHAR_SHAPE']:
            face = struct.unpack('<7H', b[0:14])
            ratio = struct.unpack('<7B', b[14:21])
            spacing = struct.unpack('<7b', b[21:28])
            size = struct.unpack('<i', b[42:46])[0]
            chars.append(dict(face=face, ratio=ratio, spacing=spacing, size=size))
        elif tag == TAG['PARA_SHAPE']:
            p1 = struct.unpack('<I', b[0:4])[0]
            ls_old = struct.unpack('<i', b[24:28])[0]
            ls_val, ls_ty = ls_old, 0
            if len(b) >= 54:
                p3 = struct.unpack('<I', b[46:50])[0]
                ls_val = struct.unpack('<I', b[50:54])[0]
                ls_ty = p3 & 0x1F
            paras.append(dict(align=(p1 >> 2) & 0x7, ls=ls_val, ls_type=ls_ty,
                              indent=struct.unpack('<i', b[12:16])[0]))
        elif tag == TAG['STYLE']:
            name, p = wstr(b, 0); eng, p = wstr(b, p)
            prop, nxt = b[p], b[p+1]; p += 2
            lang = struct.unpack('<h', b[p:p+2])[0]; p += 2
            ps, cs = struct.unpack('<HH', b[p:p+4])
            styles.append(dict(name=name, eng=eng, para=ps, char=cs))
    # 언어별 글꼴 목록 분할 (한글, 영어, 한자, 일어, 기타, 기호, 사용자)
    langs, off = {}, 0
    if mapping:
        for i, key in enumerate(['한글','영어','한자','일어','기타','기호','사용자']):
            n = mapping[1+i]; langs[key] = fonts[off:off+n]; off += n
    return dict(fonts=fonts, langs=langs, chars=chars, paras=paras, styles=styles)

def describe(info, style):
    c = info['chars'][style['char']]; p = info['paras'][style['para']]
    han = info['langs'].get('한글', [])
    lat = info['langs'].get('영어', [])
    fh = han[c['face'][0]] if c['face'][0] < len(han) else '?'
    fl = lat[c['face'][1]] if c['face'][1] < len(lat) else '?'
    return dict(name=style['name'], size=c['size']/100.0, hangul=fh, latin=fl,
                ratio=c['ratio'][0], spacing=c['spacing'][0],
                ls='%d%s' % (p['ls'], LS_TYPE.get(p['ls_type'], '?')),
                align=ALIGN.get(p['align'], '?'), indent=p['indent'])

if __name__ == '__main__':
    info = load(sys.argv[1])
    print('스타일 %d개 / 글자모양 %d개 / 문단모양 %d개' % (len(info['styles']), len(info['chars']), len(info['paras'])))
    print('한글 글꼴:', info['langs'].get('한글'))
    print()
    print('%-16s %-7s %-12s %-14s %-6s %-6s %-9s %-7s' % ('스타일','크기','한글글꼴','영문글꼴','장평','자간','줄간격','정렬'))
    for st in info['styles']:
        d = describe(info, st)
        print('%-16s %-7s %-12s %-14s %-6s %-6s %-9s %-7s' % (
            d['name'], '%.1fpt' % d['size'], d['hangul'], d['latin'],
            '%d%%' % d['ratio'], d['spacing'], d['ls'], d['align']))
