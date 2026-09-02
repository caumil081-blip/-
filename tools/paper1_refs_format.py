# -*- coding: utf-8 -*-
"""참고문헌을 KIIT 양식 표기법에 맞춘다.

양식 예시(논문양식.hwp 에서 확인):
  [1] D. W. Ryoo and C. S. Bae, "Design of The Wearable Gadgets ...",
      IEEE Transactions on Consumer Electronics, Vol. 53, No. 4,
      pp. 1477-1482, Nov. 2007.
  [1] H. K. Hartline, A. B. Smith, and F. Ratlliff, "Inhibitory interaction
      in the retina", In Handbook of Sensory Physiology, Springer-Verlag,
      pp. 381-390, 1972.                                   <- 저서
  ... Feb. 2003. https://doi.org/10.1109/MIC.2003.1167344. <- DOI 뒤 마침표
핵심: 제목 닫는 따옴표 '뒤'에 쉼표, 월 약어는 May/June/July/Sept. 형태.
"""
import re, sys
sys.path.insert(0, '.')
import relayout as R

S = 'extracted/Contents/section0.xml'
d = open(S, encoding='utf-8').read()

MONTH = [('Jul.', 'July'), ('Jun.', 'June'), ('Sep.', 'Sept.')]

# 저서는 양식의 <저서> 형식(따옴표 친 서명 + 출판사)으로 다시 쓴다
BOOK_OLD = ('[14] S. Greco, M. Ehrgott, and J. R. Figueira (eds.), Multiple Criteria '
            'Decision Analysis: State of the Art Surveys, 2nd ed., Springer, New York, '
            'NY, USA, 2016. https://doi.org/10.1007/978-1-4939-3094-4')
BOOK_NEW = ('[14] S. Greco, M. Ehrgott, and J. R. Figueira (eds.), "Multiple Criteria '
            'Decision Analysis: State of the Art Surveys", 2nd ed., Springer, New York, '
            'NY, USA, 2016. https://doi.org/10.1007/978-1-4939-3094-4.')

changed = 0
for s, e in sorted(R.paragraphs(d), reverse=True):
    para = d[s:e]
    txt = R.own_text(para).strip()
    if not re.match(r'^\[\d+\]', txt):
        continue
    new = para
    # 1) 제목 닫는 따옴표 앞의 쉼표 -> 따옴표 뒤로
    n_q = new.count(',&quot;') + new.count(',"')
    new = new.replace(',&quot;', '&quot;,').replace(',"', '",')
    # 2) 월 약어 표기
    for a, b in MONTH:
        new = new.replace(', %s ' % a, ', %s ' % b)
    # 3) DOI 뒤 마침표
    new = re.sub(r'(https://doi\.org/[^\s<]*[^\s<.])(</hp:t>)', r'\1.\2', new)
    # 4) 저서 형식
    new = new.replace(BOOK_OLD, BOOK_NEW)
    if new != para:
        d = d[:s] + new + d[e:]
        changed += 1

open(S, 'w', encoding='utf-8').write(d)
print('참고문헌 %d건 표기 정비' % changed)
for s, e in R.paragraphs(d):
    t = R.own_text(d[s:e]).strip()
    if re.match(r'^\[(1|11|13|14|19)\]', t):
        print('  ' + t)
