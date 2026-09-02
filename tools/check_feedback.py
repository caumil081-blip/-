# -*- coding: utf-8 -*-
"""심사 피드백 4개 항목이 실제로 반영됐는지 산출물에서 직접 검사한다."""
import sys, re, zipfile
sys.path.insert(0, 'hwpx')
import relayout as R

def paras(path):
    d = zipfile.ZipFile(path).read('Contents/section0.xml').decode('utf-8')
    return d, [R.own_text(d[s:e]) for s, e in R.paragraphs(d)]

def check(path, label, abs_head, col_w, pt):
    d, ts = paras(path)
    txt = [t.strip() for t in ts if t.strip()]
    print('=' * 74); print(label); print('=' * 74)

    # ① 요약 7~8줄
    body = next((t for t in txt if t.startswith(abs_head)), None)
    per = 0.90 * (1 - 0.06)                      # 장평 90%, 자간 -6
    lines = len(body) / ((col_w / pt) / per)
    print('① 요약 분량 : %d자, 단 폭 %d / %.1fpt 기준 약 %.1f줄  -> %s'
          % (len(body), col_w, pt / 100, lines, 'OK (7~8줄)' if 6.5 <= lines <= 8.4 else '확인 필요'))

    # ② 캡션 한글 제목 병기
    ko = [t for t in txt if re.match(r'^(표|그림|알고리즘) \d+\.', t)]
    en = [t for t in txt if re.match(r'^(Table|Fig\.|Algorithm) \d+\.', t)]
    def num(t):
        m = re.match(r'^(?:표|그림|알고리즘|Table|Fig\.|Algorithm) (\d+)\.', t)
        return m.group(1)
    kk = {(t.split()[0], num(t)) for t in ko}
    ek = {({'Table':'표','Fig.':'그림','Algorithm':'알고리즘'}[t.split()[0]], num(t)) for t in en}
    print('② 캡션 병기 : 한글 %d개 / 영문 %d개, 짝 %s'
          % (len(ko), len(en), 'OK (모두 대응)' if kk == ek else '불일치 %s' % (kk ^ ek)))

    # ③ 표 안 영문 표기
    tbl_en = []
    for s, e in R.paragraphs(d):
        para = d[s:e]
        if '<hp:tbl' not in para: continue
        for m in re.finditer(r'<hp:t>(.*?)</hp:t>', para, re.S):
            t = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            if re.search(r'[A-Za-z]{3,}', t) and not re.match(r'^(Table|Fig\.|Algorithm) \d', t):
                tbl_en.append(t)
    keep = {x for x in tbl_en if re.fullmatch(r'[A-Za-z0-9_.\-+()/ ]*', x)}
    print('③ 표 안 영문 : 잔존 %d건 %s' % (len(keep), sorted(keep)[:8] if keep else ''))

    # ④ 참고문헌 월 + DOI
    refs = [t for t in txt if re.match(r'^\[\d+\]', t)]
    MON = r'(Jan|Feb|Mar|Apr|May|June|July|Aug|Sept|Oct|Nov|Dec)\.? \d{4}'
    no_m = [r[:14] for r in refs if not re.search(MON, r)]
    no_d = [r[:14] for r in refs if 'doi.org/' not in r]
    bad_q = [r[:14] for r in refs if ',"' in r or ',&quot;' in r]
    print('④ 참고문헌 : %d건 / 월 누락 %s / DOI 누락 %s / 따옴표 앞 쉼표 %s'
          % (len(refs), no_m or '없음', no_d or '없음', bad_q or '없음'))
    print()

# 본문 단 폭: (용지폭 - 좌우여백 - 단간격) / 2 = (53858-5669*2-2268)/2 = 19126
# 요약은 단 나누기 전 전체 폭 = 53858 - 5669*2 = 42520
check('hwpx/KIIT_paper1_revised.hwpx', '1번 논문 (군 이메일 업무 추출)', '군 내부 이메일에는', 39956, 1000)
check('p2/KIIT_paper2_converted.hwpx', '2번 논문 (국방 데이터 상호운용성)', '국방 정보체계는', 42520, 920)
