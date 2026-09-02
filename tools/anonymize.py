# -*- coding: utf-8 -*-
"""투고논문양식(저자정보없음) 버전을 만든다.
   양식의 Section1(투고논문양식)과 1번 논문의 처리 방식을 그대로 따른다:
   저자명은 별표 표시로 바꾸고, 소속 줄과 교신저자 각주는 뺀다."""
import re, sys
sys.path.insert(0, 'hwpx')
import relayout as R

def anonymize(d, ko_authors, en_authors, drop_prefixes, drop_contains=()):
    # 저자명 문단의 글자를 별표로 (문단·서식은 그대로 두고 텍스트만 교체)
    def replace_para(d, match_text, new_text):
        for s, e in R.paragraphs(d):
            if R.own_text(d[s:e]).strip().startswith(match_text):
                para = d[s:e]
                runs = list(re.finditer(r'<hp:run\b.*?</hp:run>', para, re.S))
                keep = None
                for r in runs:
                    if '<hp:t>' in r.group(0):
                        keep = r; break
                if keep is None: return d, False
                newrun = re.sub(r'<hp:t>.*?</hp:t>', '<hp:t>%s</hp:t>' % new_text, keep.group(0), count=1, flags=re.S)
                body = ''.join(x.group(0) for x in runs)
                para2 = para.replace(body, newrun, 1)
                return d[:s] + para2 + d[e:], True
        return d, False
    d, a = replace_para(d, ko_authors, '*, *, *, *, **')
    d, b = replace_para(d, en_authors, '*, *, *, *, ***')
    removed = 0
    for pref in drop_prefixes:
        for s, e in R.paragraphs(d):
            if R.own_text(d[s:e]).strip().startswith(pref):
                d = d[:s] + d[e:]; removed += 1; break
    for key in drop_contains:
        for s, e in R.paragraphs(d):
            if key in R.own_text(d[s:e]):
                d = d[:s] + d[e:]; removed += 1; break
    return d, a, b, removed

if __name__ == '__main__':
    S = 'p2/ex/Contents/section0.xml'
    d = open(S, encoding='utf-8').read()
    d, a, b, n = anonymize(
        d,
        ko_authors='김보라',
        en_authors='Bo-Ra Kim',
        drop_prefixes=['1) 국방부', '1) Ministry of National Defense',
                       '2) Department of AI', '3) Defense AI Education College'],
        drop_contains=['Corresponding author, E-mail'])
    assert a and b, '저자명 문단을 찾지 못함'
    open('p2/ex_anon.xml', 'w', encoding='utf-8').write(d)
    print('저자명 한글/영문 별표 처리, 소속·교신저자 각주 %d개 삭제' % n)
    for s, e in R.paragraphs(d)[:10]:
        t = R.own_text(d[s:e]).strip()
        if t: print('   %r' % t[:70])
