import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt, numpy as np
from matplotlib import font_manager
for f in ['NanumGothic.ttf','NanumGothicBold.ttf']:
    font_manager.fontManager.addfont('/usr/share/fonts/truetype/nanum/'+f)
plt.rcParams['font.family']='NanumGothic'
plt.rcParams['axes.unicode_minus']=False
plt.rcParams['font.size']=13

NAVY='#1F3864'; GRAY='#8E97AB'; ORANGE='#C55A11'; BLUE='#4472C4'; GREEN='#70AD47'; TEAL='#2E9187'

# Fig.1 (1333x697) 기법별 매핑 성능
fig,ax=plt.subplots(figsize=(13.33,6.97),dpi=100)
labels=['완전 일치','편집거리','값 형식','임베딩\n(SBERT)','학습 융합\n(로지스틱)','학습 융합\n(부스팅)']
prec=[0.9950,0.9451,0.2490,0.5480,0.7200,0.8970]
rec =[0.4038,0.4716,0.9665,0.4300,0.5400,0.5860]
f1  =[0.5745,0.6292,0.3959,0.4840,0.6180,0.7095]
x=np.arange(6); w=0.26
ax.bar(x-w,prec,w,label='정밀도',color=NAVY)
ax.bar(x,  rec, w,label='재현율(후보 내)',color=GRAY)
b3=ax.bar(x+w,f1,w,label='F1',color=ORANGE)
for b,v in zip(b3,f1): ax.text(b.get_x()+b.get_width()/2,v+0.015,'%.2f'%v,ha='center',va='bottom',color=ORANGE,fontsize=12)
ax.set_ylabel('점수'); ax.set_xticks(x); ax.set_xticklabels(labels); ax.set_ylim(0,1.08)
ax.grid(axis='y',color='0.9'); ax.set_axisbelow(True)
ax.legend(loc='upper center',bbox_to_anchor=(0.5,-0.13),ncol=3,frameon=False)
fig.tight_layout(); fig.savefig('f1.png',dpi=100); plt.close(fig)

# Fig.2 (1183x672) 난이도별 재현율
fig,ax=plt.subplots(figsize=(11.83,6.72),dpi=100)
grp=['쉬운 쌍\n(이름 유사)','어려운 쌍\n(표기 다름)']
ed=[0.997,0.000]; emb=[0.695,0.211]; lf=[0.998,0.097]
x=np.arange(2); w=0.25
for off,vals,lab,c in [(-w,ed,'편집거리(문자열)',GRAY),(0,emb,'임베딩(SBERT)',NAVY),(w,lf,'학습 융합',ORANGE)]:
    bs=ax.bar(x+off,vals,w,label=lab,color=c)
    for b,v in zip(bs,vals): ax.text(b.get_x()+b.get_width()/2,v+0.012,'%.2f'%v,ha='center',va='bottom',fontsize=12)
ax.set_ylabel('정답 쌍 재현율'); ax.set_xticks(x); ax.set_xticklabels(grp); ax.set_ylim(0,1.10)
ax.grid(axis='y',color='0.9'); ax.set_axisbelow(True); ax.legend(loc='upper right')
fig.tight_layout(); fig.savefig('f2.png',dpi=100); plt.close(fig)

# Fig.3 (1404x612) 자동확정 검토량 절감
fig,axes=plt.subplots(1,2,figsize=(14.04,6.12),dpi=100)
a=axes[0]
a.pie([9,41,50],labels=['자동확정','전문가 검토','자동기각'],autopct='%d%%',startangle=90,
      colors=[NAVY,ORANGE,GRAY],counterclock=False,textprops={'fontsize':13})
a.text(0,-1.35,'(자동확정 정밀도 0.98)',ha='center',color=NAVY,fontsize=13)
b=axes[1]
vals=[29324,12024]
bs=b.bar(['전체 후보\n(AI 미적용)','사람 검토\n(제안 방법)'],vals,0.55,color=[GRAY,ORANGE])
for bb,v in zip(bs,vals): b.text(bb.get_x()+bb.get_width()/2,v+400,format(v,','),ha='center',va='bottom',fontsize=13)
b.set_ylabel('검토 대상 쌍 수'); b.set_ylim(0,33000); b.grid(axis='y',color='0.9'); b.set_axisbelow(True)
fig.tight_layout(); fig.savefig('f3.png',dpi=100); plt.close(fig)

# Fig.4 (1483x612) LLM 운영 곡선 + 검토 목록 절감
fig,axes=plt.subplots(1,2,figsize=(14.83,6.12),dpi=100)
a=axes[0]
th=np.array([0,.05,.10,.15,.20,.25,.30,.35,.40,.45,.50,.55,.60,.65,.70,.75,.80,.85,.90,.95,1.0])
pr=np.array([.089,.291,.291,.291,.291,.291,.291,.291,.575,.632,.632,.632,.632,.632,.632,.632,.632,.632,.757,.751,.0])
rc=np.array([1.0,.953,.953,.953,.953,.953,.953,.953,.745,.705,.705,.705,.705,.705,.705,.705,.705,.700,.660,.617,.0])
ff=np.array([.163,.445,.445,.445,.445,.445,.445,.445,.651,.665,.665,.665,.665,.665,.665,.665,.665,.663,.679,.676,.0])
a.plot(th,pr,'o-',color=NAVY,label='정밀도(실제 비율)',ms=5)
a.plot(th,rc,'s-',color=GRAY,label='재현율',ms=5)
a.plot(th,ff,'^-',color=ORANGE,label='F1(실제 비율)',ms=5)
a.axvline(0.90,color=ORANGE,ls='--',lw=1.6)
a.text(0.02,1.0,'π = 0.0894',color=NAVY,fontsize=12,va='center')
a.set_xlabel('LLM 확신도 임계값'); a.set_ylabel('점수'); a.set_ylim(0,1.08)
a.grid(color='0.92'); a.set_axisbelow(True); a.legend(loc='lower center',fontsize=12)
b=axes[1]
vals=[21280,1593]
bs=b.bar(['LLM 미적용\n(전수 검토)','LLM 선별 적용'],vals,0.55,color=[GRAY,TEAL])
for bb,v,h in zip(bs,vals,['적중률 9%','적중률 76%']):
    b.text(bb.get_x()+bb.get_width()/2,v+400,format(v,',')+'\n'+h,ha='center',va='bottom',fontsize=13)
b.set_ylabel('사람 검토 대상 쌍 수'); b.set_ylim(0,25500); b.grid(axis='y',color='0.9'); b.set_axisbelow(True)
fig.tight_layout(); fig.savefig('f4.png',dpi=100); plt.close(fig)

# Fig.5 (1332x732) topk 별 재현율 상한/전체 재현율
fig,ax=plt.subplots(figsize=(13.32,7.32),dpi=100)
topk=[20,40,60,100]; ceil=[0.5127,0.6603,0.7492,0.8530]; ovr=[0.3315,0.3870,0.4104,0.4370]
cand=[14690,29324,43377,70000]
ax.plot(topk,ceil,'o-',color=NAVY,label='후보 재현율 상한',ms=8)
ax.plot(topk,ovr,'s-',color=ORANGE,label='융합 전체 재현율',ms=8)
for x0,y0 in zip(topk,ceil): ax.text(x0,y0+0.025,'%.2f'%y0,ha='center',color=NAVY,fontsize=12)
ax.set_xlabel('topk(속성당 후보 수)'); ax.set_ylabel('재현율'); ax.set_ylim(0,1.0)
ax.grid(color='0.92'); ax.set_axisbelow(True)
ax2=ax.twinx()
ax2.plot(topk,cand,'^--',color=GRAY,label='후보 쌍 수(우측 축)',ms=8)
ax2.set_ylabel('후보 쌍 수',color=GRAY); ax2.tick_params(axis='y',colors=GRAY)
h1,l1=ax.get_legend_handles_labels(); h2,l2=ax2.get_legend_handles_labels()
ax.legend(h1+h2,l1+l2,loc='center right',fontsize=12)
fig.tight_layout(); fig.savefig('f5.png',dpi=100); plt.close(fig)

# Fig.6 (1333x732) 세 관점 후보 생성 재현율 상한
fig,ax=plt.subplots(figsize=(13.33,7.32),dpi=100)
labs=['의미\n(임베딩)','문자열\n(문자)','값 형식\n(인스턴스)','의미\n+문자열','의미\n+값 형식','세 관점\n합집합']
vals=[0.660,0.527,0.382,0.783,0.786,0.870]
cols=[NAVY,GRAY,TEAL,BLUE,GREEN,ORANGE]
bs=ax.bar(labs,vals,0.6,color=cols)
for b,v in zip(bs,vals): ax.text(b.get_x()+b.get_width()/2,v+0.014,'%.2f'%v,ha='center',va='bottom',fontsize=13)
ax.axhline(0.66,color='#C00000',ls='--',lw=1.8)
ax.text(2.0,0.685,'임베딩 단독 상한 0.66',color='#C00000',fontsize=13,ha='center')
ax.set_ylabel('후보 재현율 상한'); ax.set_ylim(0,1.0)
ax.grid(axis='y',color='0.92'); ax.set_axisbelow(True)
fig.tight_layout(); fig.savefig('f6.png',dpi=100); plt.close(fig)
print('done')
