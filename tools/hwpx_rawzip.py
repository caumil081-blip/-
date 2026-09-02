# -*- coding: utf-8 -*-
"""원본 HWPX의 ZIP 구조를 바이트 단위로 보존하며 일부 멤버만 교체한다."""
import struct, zlib, os

def parse_local_entries(data):
    """원본 zip을 로컬 헤더 단위로 훑어 (name, header_bytes, raw_payload, meta) 목록 반환."""
    entries, off = [], 0
    while data[off:off+4] == b'PK\x03\x04':
        (ver, flag, method, mtime, mdate, crc, csize, usize,
         nlen, elen) = struct.unpack('<HHHHHIIIHH', data[off+4:off+30])
        name = data[off+30:off+30+nlen]
        extra = data[off+30+nlen:off+30+nlen+elen]
        dstart = off+30+nlen+elen
        payload = data[dstart:dstart+csize]
        entries.append(dict(name=name.decode('utf-8'), ver=ver, flag=flag, method=method,
                            mtime=mtime, mdate=mdate, crc=crc, csize=csize, usize=usize,
                            extra=extra, payload=payload))
        off = dstart + csize
        if flag & 0x08:            # data descriptor
            if data[off:off+4] == b'PK\x07\x08': off += 4
            off += 12
    return entries

def build(orig_path, out_path, replacements):
    """replacements: {멤버이름: 새 바이트}. 나머지는 원본 압축 스트림 그대로 복사."""
    data = open(orig_path, 'rb').read()
    entries = parse_local_entries(data)
    out, central, offsets, effective = bytearray(), bytearray(), [], []

    for e in entries:
        if e['name'] in replacements:
            raw = replacements[e['name']]
            e = dict(e)
            e['crc'] = zlib.crc32(raw) & 0xFFFFFFFF
            e['usize'] = len(raw)
            if e['method'] == 8:   # deflate: 원본과 같은 방식(raw deflate, level 9)
                co = zlib.compressobj(9, zlib.DEFLATED, -15)
                e['payload'] = co.compress(raw) + co.flush()
            else:                  # stored
                e['payload'] = raw
            e['csize'] = len(e['payload'])

        effective.append(e)
        offsets.append(len(out))
        nb = e['name'].encode('utf-8')
        out += struct.pack('<IHHHHHIIIHH', 0x04034b50, e['ver'], e['flag'], e['method'],
                           e['mtime'], e['mdate'], e['crc'], e['csize'], e['usize'],
                           len(nb), len(e['extra'])) + nb + e['extra'] + e['payload']

    # central directory: 원본 central header의 부가 필드를 그대로 재사용
    import zipfile
    zf = zipfile.ZipFile(orig_path)
    cinfo = {i.filename: i for i in zf.infolist()}
    zf.close()
    for e, off in zip(effective, offsets):
        ci = cinfo[e['name']]
        nb = e['name'].encode('utf-8')
        central += struct.pack('<IHHHHHHIIIHHHHHII', 0x02014b50,
                               (ci.create_system << 8) | ci.create_version, e['ver'], e['flag'],
                               e['method'], e['mtime'], e['mdate'], e['crc'], e['csize'],
                               e['usize'], len(nb), len(e['extra']), 0, 0,
                               ci.internal_attr, ci.external_attr, off) + nb + e['extra']
    cd_off, cd_size = len(out), len(central)
    out += central
    out += struct.pack('<IHHHHIIH', 0x06054b50, 0, 0, len(entries), len(entries),
                       cd_size, cd_off, 0)
    open(out_path, 'wb').write(bytes(out))
    return len(out)

if __name__ == '__main__':
    # 검증: 아무것도 바꾸지 않고 재패키징하면 원본과 바이트 단위로 같아야 한다
    n = build('paper.hwpx', 'roundtrip.hwpx', {})
    a, b = open('paper.hwpx','rb').read(), open('roundtrip.hwpx','rb').read()
    print('원본 %d바이트 / 재패키징 %d바이트' % (len(a), len(b)))
    print('바이트 단위 동일:', a == b)
    if a != b:
        for i,(x,y) in enumerate(zip(a,b)):
            if x != y:
                print('  첫 불일치 offset', i, hex(x), hex(y)); break
