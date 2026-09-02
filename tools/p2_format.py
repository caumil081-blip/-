# -*- coding: utf-8 -*-
"""2번 논문에 KIIT 공식 양식의 서식 규격을 적용한다(1번 논문과 동일한 기준)."""
import re, sys
sys.path.insert(0, '.')
import relayout as R

H, S = 'ex/Contents/header.xml', 'ex/Contents/section0.xml'
h = open(H, encoding='utf-8').read()
d = open(S, encoding='utf-8').read()
LANGS = ['hangul','latin','hanja','japanese','other','symbol','user']

# ---------------------------------------------------------------- 1) 글꼴 추가
NEED = ['휴먼명조', '휴먼고딕', '한양중고딕', '한양견명조', '한양신명조', 'HCI Poppy', 'HCI Hollyhock', 'Times New Roman']
TTF = {'휴먼명조','휴먼고딕','Times New Roman','HCI Poppy','HCI Hollyhock'}
fid = {}                       # (lang, face) -> id
def add_fonts(m):
    lang, cnt, body = m.group(1), int(m.group(2)), m.group(3)
    have = {f.group(2): int(f.group(1)) for f in re.finditer(r'<hh:font id="(\d+)" face="([^"]*)"', body)}
    for face, i in have.items():            # 이미 있는 글꼴도 인덱스를 기록해 둔다
        fid[(lang, face)] = i
    add = ''
    for face in NEED:
        if face in have:
            fid[(lang, face)] = have[face]; continue
        fid[(lang, face)] = cnt
        add += ('<hh:font id="%d" face="%s" type="%s" isEmbedded="0">'
                '<hh:substFont face="한컴바탕" type="TTF" isEmbedded="0" binaryItemIDRef=""/>'
                '</hh:font>') % (cnt, face, 'TTF' if face in TTF else 'HFT')
        cnt += 1
    return '<hh:fontface lang="%s" fontCnt="%d">%s%s</hh:fontface>' % (lang, cnt, body, add)
h = re.sub(r'<hh:fontface lang="(\w+)" fontCnt="(\d+)">(.*?)</hh:fontface>', add_fonts, h, flags=re.S)
print('1) 글꼴 %d종 확보 (휴먼명조·휴먼고딕·한양중고딕·한양견명조·한양신명조·HCI Poppy·HCI Hollyhock·Times New Roman)' % len(NEED))

def ref(hangul, latin):
    """언어별 fontRef 문자열. 한글계열은 hangul 글꼴, 나머지는 latin 글꼴."""
    pick = {'hangul': hangul, 'latin': latin, 'hanja': hangul, 'japanese': hangul,
            'other': latin, 'symbol': latin, 'user': hangul}
    return '<hh:fontRef %s/>' % ' '.join(
        '%s="%d"' % (l, fid[(l.upper(), pick[l])]) for l in LANGS)

# ---------------------------------------------------------------- 2) 장평/자간 통일
SPACING_EXC = {}          # 아래 3)에서 제목/저자명 charPr 을 확정한 뒤 다시 적용
def uniform(m):
    blk = m.group(0)
    blk = re.sub(r'<hh:ratio [^/]*/>', '<hh:ratio %s/>' % ' '.join('%s="90"' % l for l in LANGS), blk)
    blk = re.sub(r'<hh:spacing [^/]*/>', '<hh:spacing %s/>' % ' '.join('%s="-6"' % l for l in LANGS), blk)
    return blk
h, n = re.subn(r'<hh:charPr id="\d+" .*?</hh:charPr>', uniform, h, flags=re.S)
print('2) 글자모양 %d개 -> 장평 90%%, 자간 -6' % n)

# ---------------------------------------------------------------- 3) 스타일별 글꼴/크기
def set_char(cid, hangul, latin, height=None, spacing=None):
    global h
    m = re.search(r'<hh:charPr id="%d" .*?</hh:charPr>' % cid, h, re.S)
    if not m: return False
    blk = m.group(0); new = re.sub(r'<hh:fontRef [^/]*/>', ref(hangul, latin), blk)
    if height:
        new = re.sub(r'(<hh:charPr id="%d" height=")\d+' % cid, r'\g<1>%d' % height, new)
    if spacing is not None:
        new = re.sub(r'<hh:spacing [^/]*/>',
                     '<hh:spacing %s/>' % ' '.join('%s="%d"' % (l, spacing) for l in LANGS), new)
    h = h.replace(blk, new); return True

# 논문2 charPr 용도(사전 분석):
#   10 본문/참고문헌/표 안, 19 요약본문, 18 캡션, 12 소제목, 17 장제목,
#   20 요약문제목, 11 제목(한글), 13 영문제목, 23/24 저자명, 25/16 삭제된 구분줄, 2 각주
set_char(10, '휴먼명조', 'Times New Roman', height=1000)     # 본문·참고문헌
set_char(19, '한양신명조', 'Times New Roman', height=920)     # 영문요약문
set_char(18, '한양중고딕', '한양중고딕', height=900)            # 캡션
set_char(12, '한양중고딕', '한양중고딕', height=1100)           # 소제목
set_char(17, '휴먼고딕', 'HCI Hollyhock', height=1100)        # 각 장 제목
set_char(20, '돋움', '돋움', height=1050)                     # 요약문제목/Abstract
set_char(11, '휴먼명조', 'HCI Poppy', height=1700, spacing=-7) # 한글제목
set_char(13, '한양견명조', '한양견명조', height=1500, spacing=-7) # 영문제목
set_char(23, '돋움', '돋움', height=1100, spacing=5)           # 저자명
set_char(24, '휴먼명조', 'HCI Poppy', height=1000, spacing=5)  # 영문저자명
set_char(2,  '휴먼명조', 'HCI Poppy', height=820, spacing=-8)  # 각주
print('3) 스타일별 글꼴·크기 적용 (본문 10pt/캡션 9pt/소제목·장제목 11pt/제목 17·15pt)')

# 한글 요약본문 전용 글자모양(휴먼명조/HCI Poppy 9.2pt)을 새로 추가
cnt = int(re.search(r'<hh:charProperties itemCnt="(\d+)">', h).group(1))
kor_cid = cnt
src = re.search(r'<hh:charPr id="19" .*?</hh:charPr>', h, re.S).group(0)
clone = (src.replace('<hh:charPr id="19"', '<hh:charPr id="%d"' % kor_cid, 1)
            .replace(re.search(r'<hh:fontRef [^/]*/>', src).group(0), ref('휴먼명조', 'HCI Poppy')))
h = h.replace('<hh:charProperties itemCnt="%d">' % cnt,
              '<hh:charProperties itemCnt="%d">' % (cnt + 1), 1)
h = h.replace('</hh:charProperties>', clone + '</hh:charProperties>', 1)
print('   한글 요약본문용 글자모양 %d번 추가 (휴먼명조/HCI Poppy 9.2pt)' % kor_cid)

# 한글 요약 본문 문단의 run 을 새 글자모양으로
kor = open('kor_abs.txt', encoding='utf-8').read()[:30]
for s, e in R.paragraphs(d):
    if R.own_text(d[s:e]).startswith(kor):
        d = d[:s] + re.sub(r'charPrIDRef="\d+"', 'charPrIDRef="%d"' % kor_cid, d[s:e]) + d[e:]
        break

# ---------------------------------------------------------------- 4) 문단모양(줄간격·정렬)
def set_para(pid, align=None, ls=None):
    global h
    m = re.search(r'<hh:paraPr id="%d" .*?</hh:paraPr>' % pid, h, re.S)
    if not m: return
    blk = m.group(0); new = blk
    if align: new = re.sub(r'(<hh:align horizontal=")\w+', r'\g<1>%s' % align, new)
    if ls:    new = re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>%d' % ls, new)
    h = h.replace(blk, new)

set_para(8,  align='CENTER')                 # .H1 각 장 제목 -> 가운데
set_para(9,  align='LEFT')                   # .H2 소제목 -> 왼쪽
cnt = int(re.search(r'<hh:paraProperties itemCnt="(\d+)">', h).group(1))
fig_pid, tbl_pid = cnt, cnt + 1
base = re.search(r'<hh:paraPr id="14" .*?</hh:paraPr>', h, re.S).group(0)
figp = (base.replace('<hh:paraPr id="14"', '<hh:paraPr id="%d"' % fig_pid, 1)
            .replace('horizontal="CENTER"', 'horizontal="CENTER"', 1))
figp = re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>130', figp)
tblp = (base.replace('<hh:paraPr id="14"', '<hh:paraPr id="%d"' % tbl_pid, 1)
            .replace('horizontal="CENTER"', 'horizontal="LEFT"', 1))
tblp = re.sub(r'(<hh:lineSpacing type="PERCENT" value=")\d+', r'\g<1>130', tblp)
h = h.replace('<hh:paraProperties itemCnt="%d">' % cnt,
              '<hh:paraProperties itemCnt="%d">' % (cnt + 2), 1)
h = h.replace('</hh:paraProperties>', figp + tblp + '</hh:paraProperties>', 1)

FIG = re.compile(r'^(그림|Fig\.) \d+\.'); TBL = re.compile(r'^(표|Table) \d+\.')
edits, nf, nt = [], 0, 0
for s, e in R.paragraphs(d):
    para = d[s:e]
    if '<hp:tbl' in para or '<hp:pic' in para: continue
    m = re.match(r'<hp:p [^>]*?paraPrIDRef="(\d+)" styleIDRef="6"', para)
    if not m: continue
    t = R.own_text(para).strip()
    tgt = fig_pid if FIG.match(t) else (tbl_pid if TBL.match(t) else None)
    if tgt is None: continue
    he_ = para.index('>') + 1
    edits.append((s, s + he_, re.sub(r'paraPrIDRef="\d+"', 'paraPrIDRef="%d"' % tgt, para[:he_], count=1)))
    nf += FIG.match(t) is not None; nt += TBL.match(t) is not None
for x, y, rep in sorted(edits, reverse=True):
    d = d[:x] + rep + d[y:]
print('4) 장제목 가운데 / 소제목 왼쪽 / 그림캡션 %d개 가운데 130%% / 표캡션 %d개 왼쪽 130%%' % (nf, nt))

# ---------------------------------------------------------------- 5) 줄 나눔 캐시 전량 삭제
d, nls = re.subn(r'<hp:linesegarray>.*?</hp:linesegarray>', '', d, flags=re.S)
print('5) 줄 나눔 캐시 %d개 삭제 (한글이 다시 조판)' % nls)

open(H, 'w', encoding='utf-8').write(h)
open(S, 'w', encoding='utf-8').write(d)
