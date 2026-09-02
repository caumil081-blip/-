# -*- coding: utf-8 -*-
"""1번 논문의 게재논문양식(저자정보있음) 버전을 만든다.
   저자 정보는 2번 논문과 동일(사용자 확인)."""
import re, sys
sys.path.insert(0, 'hwpx')
import relayout as R

KO_AUTHORS = '김보라1) ․ 최은원1) ․ 한상욱1) ․ 김태훈2) ․ 조진혁**,3)'
KO_AFFIL   = '1) 국방부, 2) 중앙대학교 AI학과, 3) 중앙대학교 국방AI교육대학'
EN_AUTHORS = 'Bo-Ra Kim1) ․ Eun-Won Choi1) ․ Sang-Wook Han1) ․ Taehoon Kim2) ․ Jin-Hyuk Jo**,3)'
EN_AFFILS  = ['1) Ministry of National Defense, Republic of Korea',
              '2) Department of AI, Chung-Ang University, Korea',
              '3) Defense AI Education College, Chung-Ang University, Korea']
CORRESP    = '** Corresponding author, E-mail: paikj@cau.ac.kr'

S = 'hwpx/extracted/Contents/section0.xml'
H = 'hwpx/extracted/Contents/header.xml'
d = open(S, encoding='utf-8').read(); h = open(H, encoding='utf-8').read()

def para_of(pred, limit=24):
    for k, (s, e) in enumerate(R.paragraphs(d)):
        if k > limit: break
        if pred(R.own_text(d[s:e]).strip()): return s, e
    return None

def set_text(span, text):
    """문단의 첫 텍스트 런만 남기고 내용을 교체한다."""
    global d
    s, e = span
    para = d[s:e]
    runs = [m for m in re.finditer(r'<hp:run\b.*?</hp:run>', para, re.S) if '<hp:t>' in m.group(0)]
    first = runs[0]
    new = re.sub(r'<hp:t>.*?</hp:t>', '<hp:t>%s</hp:t>' % text, first.group(0), count=1, flags=re.S)
    body = para[runs[0].start():runs[-1].end()]
    d = d[:s] + para.replace(body, new, 1) + d[e:]

def clone_after(span, text, char_id, para_id):
    """span 문단 바로 뒤에 같은 서식의 새 문단을 넣는다."""
    global d
    s, e = span
    newp = ('<hp:p id="0" paraPrIDRef="%d" styleIDRef="0" pageBreak="0" columnBreak="0" merged="0">'
            '<hp:run charPrIDRef="%d"><hp:t>%s</hp:t></hp:run></hp:p>') % (para_id, char_id, text)
    d = d[:e] + newp + d[e:]

# 소속 줄에 쓸 서식(지원기관표기와 같은 9.2pt 가운데 130%)
fund = para_of(lambda t: t.startswith('이 논문은 2026년도'))
assert fund, '지원기관표기 문단을 찾지 못함'
f_char = int(re.search(r'charPrIDRef="(\d+)"', d[fund[0]:fund[1]]).group(1))
f_para = int(re.match(r'<hp:p [^>]*?paraPrIDRef="(\d+)"', d[fund[0]:fund[1]]).group(1))

# 영문 저자명 -> 실명, 그 뒤에 영문 소속 3줄
en = para_of(lambda t: t == '*, *, *, *, ***')
assert en, '영문 저자명 문단을 찾지 못함'
set_text(en, EN_AUTHORS)
en = para_of(lambda t: t.startswith('Bo-Ra Kim'))
for line in reversed(EN_AFFILS):
    clone_after(en, line, f_char, f_para)
print('영문 저자명 + 소속 3줄 반영')

# 한글 저자명 -> 실명, 그 뒤에 한글 소속 1줄
ko = para_of(lambda t: t == '*, *, *, *, **')
assert ko, '한글 저자명 문단을 찾지 못함'
set_text(ko, KO_AUTHORS)
ko = para_of(lambda t: t.startswith('김보라'))
clone_after(ko, KO_AFFIL, f_char, f_para)
print('한글 저자명 + 소속 1줄 반영')

# 교신저자 각주: 지원기관표기 바로 뒤에 같은 서식으로
fund = para_of(lambda t: t.startswith('이 논문은 2026년도'))
clone_after(fund, CORRESP, f_char, f_para)
print('교신저자 표기 추가')

open(S, 'w', encoding='utf-8').write(d)
for k, (s, e) in enumerate(R.paragraphs(d)[:16]):
    t = R.own_text(d[s:e]).strip()
    if t: print('   %s' % t[:78])
