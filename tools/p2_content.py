# -*- coding: utf-8 -*-
"""2번 논문: 캡션 한글 병기, 표 안 한글화, 본문 상호참조, 참고문헌 정비."""
import re, sys
sys.path.insert(0, '.')
import relayout as R

S = 'ex/Contents/section0.xml'
d = open(S, encoding='utf-8').read()
def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

# ---------------------------------------------------------------- 1) 캡션 한글 병기
CAPTIONS = [
 ('Table 1. Composition of the synthetic dataset',            '표 1. 합성 데이터셋 구성'),
 ('Table 2. Mapping performance by method',                   '표 2. 기법별 매핑 성능'),
 ('Fig. 1. Mapping performance by method',                    '그림 1. 기법별 매핑 성능'),
 ('Table 3. Recall of gold pairs by difficulty',              '표 3. 난이도별 정답 쌍 재현율'),
 ('Fig. 2. Recall of gold pairs by difficulty',               '그림 2. 난이도별 정답 쌍 재현율'),
 ('Table 4. High-precision auto-confirmation operating points','표 4. 고정밀 자동확정 운영 지점'),
 ('Fig. 3. Review workload reduction with auto-confirmation', '그림 3. 자동확정에 따른 검토량 절감'),
 ('Table 5. Manual review queue for hard candidates',         '표 5. 어려운 후보의 사람 검토 목록'),
 ('Fig. 4. LLM operating curve and review queue reduction',   '그림 4. LLM 운영 곡선과 검토 목록 절감'),
 ('Table 6. Performance by candidate size (topk)',            '표 6. 후보 수(topk)별 성능'),
 ('Fig. 5. Recall ceiling and overall recall by topk',        '그림 5. topk별 재현율 상한과 전체 재현율'),
 ('Table 7. Recall ceiling by candidate generation view',     '표 7. 후보 생성 관점별 재현율 상한'),
 ('Fig. 6. Recall ceiling with multi-view candidate generation','그림 6. 세 관점 후보 생성의 재현율 상한'),
]
SENT = {}
for n, (en, ko) in enumerate(CAPTIONS):
    needle = '<hp:t>%s</hp:t>' % en
    assert d.count(needle) == 1, '캡션 %r %d건' % (en, d.count(needle))
    i = d.find(needle)
    ps = d.rfind('<hp:p ', 0, i); pe = d.find('</hp:p>', i) + 7
    para = d[ps:pe]
    mark = 'ZCAP%02dZ' % n; SENT[mark] = en
    d = d[:ps] + para.replace(needle, '<hp:t>%s</hp:t>' % ko) \
               + para.replace(needle, '<hp:t>%s</hp:t>' % mark) + d[pe:]
print('1) 캡션 %d개 한글 제목 병기 (표 7 + 그림 6)' % len(CAPTIONS))

# ---------------------------------------------------------------- 2) 표 안 영문 -> 한글
CELLS = [
 ('Item','구분'), ('Value','값'), ('# Attributes','속성 수'), ('# Systems','정보체계 수'),
 ('30 (personnel, logistics, etc.)','30 (인사·군수 등)'), ('# Concepts','개념 수'),
 ('Gold mapping pairs','정답 매핑 쌍'), ('(identical 1,738 / synonym 5,725)','(동일 표기 1,738 / 동의어 5,725)'),
 ('Labeled pairs (train/eval)','라벨 쌍 (학습/평가)'), ('(match 5,000 / non-match 5,000)','(일치 5,000 / 불일치 5,000)'),
 ('method','기법'), ('precision','정밀도'), ('recall ','재현율'), ('(in-candidate)','(후보 내)'),
 ('recall (overall)','재현율 (전체)'), ('exact match','완전 일치'), ('edit distance','편집거리'),
 ('value format','값 형식'), ('embedding only(SBERT)','임베딩 단독(SBERT)'),
 ('learned fusion(logistic)','학습 융합(로지스틱)'), ('learned fusion(boosting)','학습 융합(부스팅)'),
 ('difficulty','난이도'), ('# gold pairs','정답 쌍 수'), ('embedding','임베딩'), ('(SBERT)','(SBERT)'),
 ('learned fusion','학습 융합'), ('easy pairs','쉬운 쌍'), ('(similar names)','(이름 유사)'),
 ('hard pairs','어려운 쌍'), ('(different names)','(표기 다름)'),
 ('target precision','목표 정밀도'), ('auto-confirmed pairs','자동확정 쌍'),
 ('recovered gold pairs','회수한 정답 쌍'), ('ratio of gold','정답 대비 비율'),
 ('review queue','검토 목록'), ('hit rate','적중률'), ('gold found','찾은 정답'),
 ('w/o LLM(all)','LLM 미적용(전수)'), ('LLM-filtered','LLM 선별'),
 ('candidates','후보 수'), ('recall ceiling','재현율 상한'), ('fusion F1','융합 F1'),
 ('fusion precision','융합 정밀도'), ('overall recall','전체 재현율'),
 ('candidate generation view','후보 생성 관점'), ('semantic(embedding)','의미(임베딩)'),
 ('string(char)','문자열(문자)'), ('value format(instance)','값 형식(인스턴스)'),
 ('semantic+string','의미+문자열'), ('semantic+value format','의미+값 형식'),
 ('union of 3 views','세 관점 합집합'),
]
n_cell = 0
for en, ko in CELLS:
    needle = '<hp:t>%s</hp:t>' % en
    c = d.count(needle)
    if c == 0: continue
    d = d.replace(needle, '<hp:t>%s</hp:t>' % ko); n_cell += c
print('2) 표 안 영문 표기 %d곳 한글화' % n_cell)

# ---------------------------------------------------------------- 3) 본문 상호참조
d = re.sub(r'Table (\d+)', r'표 \1', d)
d = re.sub(r'Fig\. (\d+)', r'그림 \1', d)
print('3) 본문 상호참조 Table N / Fig. N -> 표 N / 그림 N')

for mark, en in SENT.items():
    assert mark in d
    d = d.replace(mark, en)
open(S, 'w', encoding='utf-8').write(d)
