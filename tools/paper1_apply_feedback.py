# -*- coding: utf-8 -*-
import re, io, sys

SRC = 'extracted/Contents/section0.xml'
d = open(SRC, encoding='utf-8').read()
orig = d

# ---------------------------------------------------------------
# 1) 요약 본문 축약 (7~8줄)
# ---------------------------------------------------------------
OLD_ABS = ('군에서는 지시·보고 요청·자료 제출 같은 행정 업무가 내부 이메일로 쉼 없이 오가며, 업무 목적과 마감이 본문 곳곳에 '
 '흩어져 있어 수신자가 일일이 해석해 우선순위를 정해야 한다. 본 논문은 데이터를 외부로 보내지 않는 로컬 대규모 언어모델(LLM)로 '
 '업무 정보를 구조화해 추출하고, 기한·발신자 권한·업무유형을 가중 결합한 규칙 엔진으로 우선순위를 매기는 시스템을 제안한다. '
 '합성 군 이메일 1,150건에서 정규식·휴리스틱·LLM(qwen2.5:7b)을 실행해 평가한 결과 LLM은 업무 탐지 F1 0.979(정밀도 1.000), '
 '업무유형 macro-F1 0.902를 기록하였고, 우선순위 엔진은 가중치가 바뀌어도 안정적인 3등급 순위를 제시하였다. 계층화 분석은 '
 '암시적 마감의 재현율을 후단 규칙 기반 날짜 정규화가 제한함을 밝혀 개선 지점을 지목한다.')

NEW_ABS = ('군 내부 이메일에는 지시·보고 요청·자료 제출과 같은 행정 업무가 마감과 함께 흩어져 있어 수신자가 일일이 해석해 '
 '우선순위를 정해야 한다. 본 논문은 데이터를 외부로 보내지 않는 로컬 대규모 언어모델(LLM)로 업무 정보를 구조화해 추출하고, '
 '기한·발신자 권한·업무유형을 가중 결합한 규칙 엔진으로 우선순위를 산정하는 시스템을 제안한다. 합성 군 이메일 1,150건을 '
 '대상으로 평가한 결과 LLM(qwen2.5:7b)은 업무 탐지 F1 0.979, 업무유형 macro-F1 0.902를 기록하였고, 우선순위 엔진은 '
 '가중치 변화에도 안정적인 3등급 순위를 제시하였다. 계층화 분석은 암시적 마감의 재현율 한계가 후단 규칙 기반 날짜 정규화에 '
 '있음을 밝혀 개선 지점을 지목한다.')

assert OLD_ABS in d, 'abstract not found'
# 요약 문단 전체(<hp:p>...</hp:p>)를 찾아 linesegarray 를 새 길이에 맞게 정리
i = d.find(OLD_ABS)
ps = d.rfind('<hp:p ', 0, i)
pe = d.find('</hp:p>', i) + len('</hp:p>')
para = d[ps:pe]
para_new = para.replace(OLD_ABS, NEW_ABS)
# 새 본문 길이를 넘어서는 lineseg 제거
segs = re.findall(r'<hp:lineseg [^/]*?/>', para_new)
keep = [s for s in segs if int(re.search(r'textpos="(\d+)"', s).group(1)) < len(NEW_ABS)]
para_new = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>',
                  '<hp:linesegarray>' + ''.join(keep) + '</hp:linesegarray>',
                  para_new, flags=re.S)
d = d[:ps] + para_new + d[pe:]
print('요약: %d자 -> %d자, lineseg %d -> %d' % (len(OLD_ABS), len(NEW_ABS), len(segs), len(keep)))

# ---------------------------------------------------------------
# 2) 표/그림/알고리즘 캡션에 한글 제목 병기
# ---------------------------------------------------------------
CAPTIONS = [
 ('Table 1. Comparison with prior work',                            '표 1. 선행 연구와의 비교'),
 ('Fig. 1. Overall architecture of the proposed system',            '그림 1. 제안 시스템의 전체 구조'),
 ('Table 2. Extracted core fields',                                 '표 2. 추출 대상 핵심 필드'),
 ('Algorithm 1. Deadline normalization',                            '알고리즘 1. 마감 표현 정규화'),
 ('Table 3. Deadline score rules',                                  '표 3. 기한 점수 산정 규칙'),
 ('Table 4. Rank-based score rules',                                '표 4. 계급 기반 점수 산정 규칙'),
 ('Table 5. Task-type score rules',                                 '표 5. 업무유형 점수 산정 규칙'),
 ('Table 6. Priority score components and weights',                 '표 6. 우선순위 점수의 구성 요소와 가중치'),
 ('Algorithm 2. Priority scoring and grading',                      '알고리즘 2. 우선순위 점수 산정 및 등급화'),
 ('Table 7. Dataset composition',                                   '표 7. 데이터셋 구성'),
 ('Table 8. Extraction performance comparison (F1 / accuracy)',     '표 8. 추출 성능 비교(F1 / 정확도)'),
 ('Fig. 2. Extraction performance comparison across methods',       '그림 2. 방법별 추출 성능 비교'),
 ('Table 9. Per-class task-type F1 by method',                      '표 9. 방법별 업무유형 F1 점수'),
 ('Table 10. Deadline detection recall by phrasing style',          '표 10. 마감 표현 유형별 검출 재현율'),
 ('Fig. 3. Deadline detection recall by phrasing style',            '그림 3. 마감 표현 유형별 검출 재현율'),
 ('Table 11. Grade distribution',                                   '표 11. 우선순위 등급 분포'),
 ('Fig. 4. Mean component scores by priority grade',                '그림 4. 등급별 점수 요소 평균'),
 ('Table 12. Weight sensitivity (ablation)',                        '표 12. 가중치 민감도 분석'),
 ('Fig. 5. Grade distribution under different weight configurations','그림 5. 가중치 구성별 등급 분포'),
]

SENTINEL = {}
for n, (en, ko) in enumerate(CAPTIONS):
    marker = 'CAP%02d' % n
    needle = '<hp:t>%s</hp:t>' % en
    assert d.count(needle) == 1, 'caption not unique: ' + en
    i = d.find(needle)
    ps = d.rfind('<hp:p ', 0, i)
    pe = d.find('</hp:p>', i) + len('</hp:p>')
    para = d[ps:pe]
    # 한글 캡션 문단: 동일 서식, lineseg 는 첫 줄만 남김
    ko_para = para.replace(needle, '<hp:t>%s</hp:t>' % ko)
    ksegs = re.findall(r'<hp:lineseg [^/]*?/>', ko_para)
    ko_para = re.sub(r'<hp:linesegarray>.*?</hp:linesegarray>',
                     '<hp:linesegarray>' + (ksegs[0] if ksegs else '') + '</hp:linesegarray>',
                     ko_para, flags=re.S)
    # 영문 캡션 문단은 본문 상호참조 치환에서 보호
    en_para = para.replace(needle, '<hp:t>%s</hp:t>' % marker)
    SENTINEL[marker] = en
    d = d[:ps] + ko_para + en_para + d[pe:]
print('캡션 %d개 한글 제목 병기 완료' % len(CAPTIONS))

# ---------------------------------------------------------------
# 3) 표 내부 영문 표기 -> 한글 표기
# ---------------------------------------------------------------
CELL = [
 ('<hp:t>Regex</hp:t>',     '<hp:t>정규식</hp:t>',   3),
 ('<hp:t>Heuristic</hp:t>', '<hp:t>휴리스틱</hp:t>', 3),
 ('<hp:t>Spear.</hp:t>',    '<hp:t>순위상관</hp:t>', 1),
 ('<hp:t>ML 분류</hp:t>',   '<hp:t>기계학습 분류</hp:t>', 1),
 ('<hp:t>AHP[13]</hp:t>',   '<hp:t>계층분석법[13]</hp:t>', 1),
 ('<hp:t> NER</hp:t>',      '<hp:t> 개체명 인식</hp:t>', 1),
 ('<hp:t>유형 macro-F1</hp:t>', '<hp:t>유형 macro-F1</hp:t>', 1),
]
for old, new, cnt in CELL:
    assert d.count(old) == cnt, 'cell count mismatch %r: %d != %d' % (old, d.count(old), cnt)
    d = d.replace(old, new)
print('표 셀 한글화 완료')

# ---------------------------------------------------------------
# 4) 알고리즘 의사코드의 서술 표기 한글화
# ---------------------------------------------------------------
ALG = [
 ('Input: deadline text, reference time now', '입력: 마감 원문 s, 기준 시각 now'),
 ('Output: ISO datetime, or None',            '출력: ISO 8601 일시 또는 None'),
 ('▷ unresolved → no-deadline',               '▷ 해석 실패 → 마감 없음'),
 ('Input: fields (b,k,u,τ,d), now, weights (w_D,w_A,w_T)',
  '입력: 필드 (b,k,u,τ,d), 기준 시각 now, 가중치 (w_D,w_A,w_T)'),
 ('Output: (P, grade) or SKIP',               '출력: (P, 등급) 또는 SKIP'),
 ('▷ non-task',                               '▷ 비업무'),
 ('grade ← Immediate',                        'grade ← 지금 바로'),
 ('grade ← Today',                            'grade ← 오늘 안에'),
 ('grade ← Deferred',                         'grade ← 대기 가능'),
]
for old, new in ALG:
    assert d.count(old) == 1, 'alg text not unique: %r (%d)' % (old, d.count(old))
    d = d.replace(old, new)
print('알고리즘 표기 한글화 완료')

# ---------------------------------------------------------------
# 5) 본문 상호참조 Table N / Fig. N / Algorithm N -> 표 N / 그림 N / 알고리즘 N
# ---------------------------------------------------------------
before = d
d = re.sub(r'Table (\d+)', r'표 \1', d)
d = re.sub(r'Fig\. (\d+)', r'그림 \1', d)
d = re.sub(r'Algorithm (\d+)', r'알고리즘 \1', d)
print('본문 상호참조 치환: %d곳' % len(re.findall(r'표 \d+|그림 \d+|알고리즘 \d+', d)))

# 보호해 둔 영문 캡션 복원
for marker, en in SENTINEL.items():
    assert marker in d
    d = d.replace(marker, en)

open(SRC, 'w', encoding='utf-8').write(d)
print('OK', len(orig), '->', len(d))
