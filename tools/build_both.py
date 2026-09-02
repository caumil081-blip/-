# -*- coding: utf-8 -*-
import sys, zipfile, re, xml.etree.ElementTree as ET
sys.path.insert(0, 'hwpx')
import relayout as R, rawzip

def build(base, outdir, out, extra):
    src = zipfile.ZipFile(base)
    rep = dict(extra)
    rep['Contents/section0.xml'] = open(outdir + '/Contents/section0.xml', 'rb').read()
    rep['Contents/header.xml']   = open(outdir + '/Contents/header.xml', 'rb').read()
    rawzip.build(base, out, rep)
    z = zipfile.ZipFile(out)
    assert z.testzip() is None and z.namelist() == src.namelist()
    assert z.read('mimetype') == b'application/hwp+zip'
    assert z.getinfo('mimetype').compress_type == zipfile.ZIP_STORED
    for nm in z.namelist():
        if nm.endswith(('.xml', '.hpf')): ET.fromstring(z.read(nm))
        assert z.read(nm) == (rep[nm] if nm in rep else src.read(nm))
    h = z.read('Contents/header.xml').decode('utf-8')
    d = z.read('Contents/section0.xml').decode('utf-8')
    pids = set(re.findall(r'<hh:paraPr id="(\d+)"', h))
    assert len(pids) == int(re.search(r'<hh:paraProperties itemCnt="(\d+)">', h).group(1))
    assert set(re.findall(r'paraPrIDRef="(\d+)"', d)) <= pids
    cids = set(re.findall(r'<hh:charPr id="(\d+)"', h))
    assert len(cids) == int(re.search(r'<hh:charProperties itemCnt="(\d+)">', h).group(1))
    assert set(re.findall(r'charPrIDRef="(\d+)"', d)) <= cids
    for m in re.finditer(r'<hh:fontface lang="(\w+)" fontCnt="(\d+)">(.*?)</hh:fontface>', h, re.S):
        assert len(re.findall(r'<hh:font id="\d+" face=', m.group(3))) == int(m.group(2))
    assert '<hp:linesegarray>' not in d
    # 오타 재검사
    bad = []
    for s, e in R.paragraphs(d):
        t = R.own_text(d[s:e]).strip()
        if not t: continue
        if re.search(r'RS-\s+\d', t): bad.append('RS- 공백')
        if re.search(r'[가-힣],[가-힣]', t): bad.append('쉼표 뒤 공백')
        if t.startswith('이 논문은') and t.count('(') != t.count(')'): bad.append('감사글 괄호')
    assert not bad, bad
    print('%-34s 검증 통과 (%d바이트)' % (out.split('/')[-1], len(open(out, 'rb').read())))

ABS1 = open('hwpx/new_abs.txt', encoding='utf-8').read()
prv1 = zipfile.ZipFile('hwpx/paper.hwpx').read('Preview/PrvText.txt').decode('utf-8')
i = prv1.find('군에서는 지시'); j = prv1.find('Abstract', i)
prv1 = prv1[:i] + ABS1 + prv1[j:]
extra1 = {'Preview/PrvText.txt': prv1.encode('utf-8')}
for n, f in [(2, 'fig2_ko.png'), (3, 'fig3_ko.png'), (4, 'fig4_ko.png'), (5, 'fig5_ko.png')]:
    extra1['BinData/image%d.png' % n] = open('hwpx/' + f, 'rb').read()
build('hwpx/paper.hwpx', 'hwpx/extracted', 'hwpx/KIIT_paper1_revised.hwpx', extra1)

kor = open('p2/kor_abs.txt', encoding='utf-8').read()
prv2 = zipfile.ZipFile('p2/paper2.hwpx').read('Preview/PrvText.txt').decode('utf-8')
i = prv2.find('Abstract')
if i > 0: prv2 = prv2[:i] + '요  약' + kor + prv2[i:]
extra2 = {'Preview/PrvText.txt': prv2.encode('utf-8')}
for n in range(1, 7):
    extra2['BinData/image%d.png' % n] = open('p2/f%d.png' % n, 'rb').read()
build('p2/paper2.hwpx', 'p2/ex', 'p2/KIIT_paper2_converted.hwpx', extra2)
