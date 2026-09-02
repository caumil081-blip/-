import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

fp = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
font_manager.fontManager.addfont(fp)
font_manager.fontManager.addfont('/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf')
plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 15

methods = ['정규식', '휴리스틱', 'LLM']
x = np.arange(3)
w = 0.38

# ---- Fig. 2 : 추출 성능 비교 (image2.png, 1644x948) ----
fig, ax = plt.subplots(figsize=(8.22, 4.74), dpi=200)
det  = [0.893, 0.990, 0.979]
typ  = [0.862, 0.913, 0.902]
b1 = ax.bar(x - w/2, det, w, label='업무 탐지 (F1)', color='#4472C4')
b2 = ax.bar(x + w/2, typ, w, label='업무유형 분류 (macro-F1)', color='#E1A33A')
for b, v in list(zip(b1, det)) + list(zip(b2, typ)):
    ax.text(b.get_x() + b.get_width()/2, v + 0.015, f'{v:.2f}', ha='center', va='bottom', fontsize=14)
ax.set_ylabel('F1 점수')
ax.set_xticks(x); ax.set_xticklabels(methods)
ax.set_ylim(0, 1.12)
ax.grid(axis='y', color='0.85', linewidth=0.8)
ax.set_axisbelow(True)
ax.legend(loc='lower right', fontsize=13.5)
fig.tight_layout()
fig.savefig('fig2_ko.png', dpi=200)
plt.close(fig)

# ---- Fig. 3 : 마감 표현 유형별 검출률 (image3.png, 1584x940) ----
fig, ax = plt.subplots(figsize=(7.92, 4.70), dpi=200)
exp = [0.746, 1.000, 1.000]
imp = [0.000, 0.259, 0.259]
b1 = ax.bar(x - w/2, exp, w, label='명시적 마감', color='#4472C4')
b2 = ax.bar(x + w/2, imp, w, label='암시적 마감', color='#C0504D')
for b, v in list(zip(b1, exp)) + list(zip(b2, imp)):
    ax.text(b.get_x() + b.get_width()/2, v + 0.015, f'{v:.2f}', ha='center', va='bottom', fontsize=14)
ax.set_ylabel('마감 검출 재현율')
ax.set_xticks(x); ax.set_xticklabels(methods)
ax.set_ylim(0, 1.15)
ax.grid(axis='y', color='0.85', linewidth=0.8)
ax.set_axisbelow(True)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.16), ncol=2, fontsize=13.5)
fig.tight_layout()
fig.savefig('fig3_ko.png', dpi=200)
plt.close(fig)

# ---- Fig. 4 : 등급별 점수 요소 평균 (image4.png, 1584x944) ----
fig, ax = plt.subplots(figsize=(7.92, 4.72), dpi=200)
grades = ['지금 바로', '오늘 안에', '대기 가능']
D = [94.17, 78.83, 38.59]
A = [72.35, 63.98, 61.90]
T = [77.94, 73.44, 73.62]
xg = np.arange(3); ww = 0.26
ax.bar(xg - ww, D, ww, label='기한 D(t)', color='#C0504D')
ax.bar(xg,      A, ww, label='권한 A(t)', color='#4472C4')
ax.bar(xg + ww, T, ww, label='유형 T(t)', color='#3E9C63')
ax.set_ylabel('점수 요소 평균')
ax.set_xticks(xg); ax.set_xticklabels(grades)
ax.grid(axis='y', color='0.85', linewidth=0.8)
ax.set_axisbelow(True)
ax.set_ylim(0, 105)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.16), ncol=3, fontsize=13.5)
fig.tight_layout()
fig.savefig('fig4_ko.png', dpi=200)
plt.close(fig)

# ---- Fig. 5 : 가중치 구성별 등급 분포 (image5.png, 1763x977) ----
fig, ax = plt.subplots(figsize=(8.82, 4.89), dpi=200)
cfgs = ['기본\n.5/.3/.2', '균등\n.33/.33/.33', '기한 강조\n.6/.2/.2', '권한 강조\n.3/.5/.2']
now  = np.array([229, 143, 297, 128])
tod  = np.array([337, 461, 270, 439])
defr = np.array([434, 396, 433, 433])
xc = np.arange(4)
ax.bar(xc, now,  0.62, label='지금 바로', color='#C0504D')
ax.bar(xc, tod,  0.62, bottom=now, label='오늘 안에', color='#E1A33A')
ax.bar(xc, defr, 0.62, bottom=now+tod, label='대기 가능', color='#3E9C63')
ax.set_ylabel('이메일 건수')
ax.set_xticks(xc); ax.set_xticklabels(cfgs)
ax.grid(axis='y', color='0.85', linewidth=0.8)
ax.set_axisbelow(True)
ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1.14), ncol=3, fontsize=13.5)
fig.tight_layout()
fig.savefig('fig5_ko.png', dpi=200)
plt.close(fig)
print('done')
