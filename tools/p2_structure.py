# -*- coding: utf-8 -*-
"""KIMST 양식 논문을 KIIT 양식 구조로 바꾼다(내용/구조 부분)."""
import re, sys
sys.path.insert(0, '.')
import relayout as R

S = 'ex/Contents/section0.xml'
d = open(S, encoding='utf-8').read()

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

# ---------------------------------------------------------------- 1) 판형
d = d.replace('<hp:margin header="3969" footer="3402" gutter="0" left="4252" right="4252" top="4252" bottom="4252"/>',
              '<hp:margin header="2835" footer="0" gutter="0" left="5669" right="5669" top="4961" bottom="4961"/>')
assert 'left="5669"' in d
print('1) 판형 -> 190x260mm, 여백 좌우20 상하17.5 머리말10 꼬리말0 (KIIT 규격)')

# ---------------------------------------------------------------- 2) KIMST 고유 요소 삭제
DROP = ['Journal of the KIMST, Vol. XX, No. X, pp. XX-XX, 20XX',
        'DOI https://doi.org/10.9766/KIMST.20XX.XX.X.XXX',
        'Research Paper       정보·통신 부문',
        '(Received XX Month 20XX / Revised XX Month 20XX / Accepted XX Month 20XX)',
        'Copyright ⓒ The Korea Institute of Military Science and Technology']
removed = []
for key in DROP:
    hit = None
    for s, e in R.paragraphs(d):
        if key in R.own_text(d[s:e]):
            hit = (s, e); break
    assert hit, '못 찾음: ' + key
    d = d[:hit[0]] + d[hit[1]:]
    removed.append(key[:42])
print('2) KIMST 고유 요소 %d개 삭제' % len(removed))
for x in removed: print('     - ' + x)


# ---------------------------------------------------------------- 2-1) 중복 문단 삭제
# 서론 첫 문단 바로 뒤에 거의 같은 내용의 초고 문단이 하나 더 남아 있었다.
# 주의: 이 텍스트는 교신저자 각주 상자(표)와 '같은 문단' 안에 들어 있으므로
#       문단을 통째로 지우면 각주 상자까지 사라진다. 텍스트만 제거한다.
DUP = '국방에는 인사·군수·정보·지휘통제·수송처럼 분야마다 각기 만든 정보체계가 많다.'
hit = None
for s0, e0 in R.paragraphs(d):
    if R.own_text(d[s0:e0]).strip().startswith(DUP):
        hit = (s0, e0); break
assert hit, '중복 문단을 찾지 못함'
para = d[hit[0]:hit[1]]
own = [para[a:b] for a, b in R.own_parts(para)]
targets = [t for seg in own for t in re.findall(r'<hp:t>.*?</hp:t>', seg, re.S)]
assert len(targets) == 1, '깊이0 텍스트가 %d개' % len(targets)
d = d[:hit[0]] + para.replace(targets[0], '', 1) + d[hit[1]:]
print('2-1) 서론의 중복 텍스트 제거 (각주 상자는 보존)')

# ---------------------------------------------------------------- 3) 한글 요약 신설
KOR_ABS = open('kor_abs.txt', encoding='utf-8').read()

ai = d.find('<hp:t>Abstract</hp:t>')
hs = d.rfind('<hp:p ', 0, ai); he = d.find('</hp:p>', ai) + 7
head_tpl = d[hs:he]
# Abstract 본문 문단
bi = d.find('Defense information systems built separately')
bs = d.rfind('<hp:p ', 0, bi); be = d.find('</hp:p>', bi) + 7
body_tpl = d[bs:be]
kor_head = head_tpl.replace('<hp:t>Abstract</hp:t>', '<hp:t>요  약</hp:t>')
old_body = re.search(r'<hp:t>(.*?)</hp:t>', body_tpl, re.S).group(1)
kor_body = body_tpl.replace('<hp:t>%s</hp:t>' % old_body, '<hp:t>%s</hp:t>' % esc(KOR_ABS))
d = d[:hs] + kor_head + kor_body + d[hs:]
print('3) 한글 요약 신설 (%d자) — 요약문제목 + 요약본문' % len(KOR_ABS))

# ---------------------------------------------------------------- 4) Keywords
OLD_KW = ('Key Words : Data Interoperability(데이터 상호운용성), Schema Matching(스키마 매칭), '
          'Sentence Embedding(문장 임베딩), Large Language Model(대규모 언어모델), '
          'Human-in-the-Loop(인간참여 검증), Defense Data(국방 데이터)')
NEW_KW = ('Keywords : data interoperability, schema matching, sentence embedding, '
          'large language model, human-in-the-loop, defense data')
assert esc(OLD_KW) in d
d = d.replace(esc(OLD_KW), esc(NEW_KW))
print('4) Keywords -> 영문 소문자 6개 (양식: 영문만, 소문자, 4~6개)')

# ---------------------------------------------------------------- 5) 장 번호 로마자
ROMAN = [('1. 서 론', 'Ⅰ. 서 론'), ('2. 관련 연구', 'Ⅱ. 관련 연구'),
         ('3. 문제 정의 및 제안 방법', 'Ⅲ. 문제 정의 및 제안 방법'), ('4. 실험 방법', 'Ⅳ. 실험 방법'),
         ('5. 실험 결과', 'Ⅴ. 실험 결과'), ('6. 논 의', 'Ⅵ. 논 의'), ('7. 결 론', 'Ⅶ. 결 론')]
for a, b in ROMAN:
    n = d.count('<hp:t>%s</hp:t>' % a)
    assert n == 1, '%r %d건' % (a, n)
    d = d.replace('<hp:t>%s</hp:t>' % a, '<hp:t>%s</hp:t>' % b)
print('5) 장 번호 %d개 로마자화 (1. -> Ⅰ.)' % len(ROMAN))

open(S, 'w', encoding='utf-8').write(d)
