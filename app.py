import base64
from io import BytesIO
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak

st.set_page_config(page_title='PetroAI Analyzer', page_icon='🔥', layout='wide')
RED='#ff2b1f'; ORANGE='#ff8a00'; BLACK='#050608'; PANEL='#0b1016'; MUTED='#9aa6b2'
ASSET=Path(__file__).parent/'assets'/'petroai_header.png'
uri=''
if ASSET.exists(): uri='data:image/png;base64,'+base64.b64encode(ASSET.read_bytes()).decode()

st.markdown(f'''<style>
.stApp{{background:radial-gradient(circle at 85% 0%,rgba(255,72,0,.12),transparent 28%),#050608;color:#f5f7fa}}
[data-testid="stHeader"]{{background:transparent}}[data-testid="stToolbar"]{{visibility:hidden}}footer{{visibility:hidden}}
.block-container{{max-width:1500px;padding-top:1rem}}
section[data-testid="stSidebar"]{{background:linear-gradient(180deg,#06080b,#0b0e13 70%,#160a06);border-right:1px solid rgba(255,70,30,.25)}}
.brand{{padding:8px 6px 18px;border-bottom:1px solid #222;margin-bottom:15px}}.brand-title{{font-size:30px;font-weight:900}}.brand-title span{{color:{RED}}}.brand-sub{{font-size:11px;color:{MUTED}}}
.hero{{min-height:155px;border:1px solid rgba(255,78,35,.55);border-radius:16px;overflow:hidden;background-image:linear-gradient(90deg,rgba(3,5,8,.98),rgba(3,5,8,.78) 38%,rgba(3,5,8,.25) 78%,rgba(3,5,8,.7)),url('{uri}');background-size:cover;background-position:center;margin-bottom:14px}}
.hero-inner{{padding:26px 28px}}.hero h1{{font-size:42px;margin:2px 0}}.hero h1 span{{color:{RED}}}.hero p{{color:#b7c0c9;max-width:650px}}.tag{{font-weight:800;font-style:italic;color:#fff}}
.asset{{display:inline-block;background:rgba(4,7,10,.8);border:1px solid #30343a;border-radius:9px;padding:7px 11px;margin:8px 5px 0 0;font-size:12px}}
.card,.panel{{background:linear-gradient(145deg,#0c1218,#070a0e);border:1px solid rgba(255,255,255,.09);border-radius:13px;padding:16px;box-shadow:0 7px 25px rgba(0,0,0,.18)}}.card{{min-height:100px;border-top:2px solid {RED}}}.orange{{border-top-color:{ORANGE}}}.label{{font-size:11px;color:#aeb8c2}}.value{{font-size:27px;font-weight:900;margin-top:5px}}.note{{font-size:11px;color:{MUTED}}}
.finding{{border:1px solid rgba(255,64,35,.45);background:rgba(255,45,20,.06);border-radius:10px;padding:12px;margin:7px 0}}.finding b{{color:#ff9b22}}
.footer{{border-top:1px solid #20252a;margin-top:28px;padding-top:12px;color:#78838f;font-size:11px}}.section-title{{font-size:19px;font-weight:900;margin:22px 0 10px;padding-left:10px;border-left:4px solid #ff2b1f}}.risk-score{{display:flex;align-items:baseline;gap:6px;margin:8px 0}}.risk-number{{font-size:48px;font-weight:900;color:#ff6a00}}.risk-badge{{display:inline-block;background:linear-gradient(90deg,#ff2b1f,#ff8a00);padding:5px 12px;border-radius:20px;font-size:11px;font-weight:900;margin-bottom:8px}}.mini-risk{{font-size:11px;border-bottom:1px solid #252b31;padding:7px 0;color:#d6dde4}}.action{{font-size:11px;color:#c8d0d8;padding:5px 0}}.trend-card{{background:#0b1016;border:1px solid rgba(255,255,255,.09);border-radius:12px;padding:13px;border-top:2px solid #ff8a00}}.trend-bad{{border-top-color:#ff2b1f}}.trend-good{{border-top-color:#ff8a00}}.trend-neutral{{border-top-color:#64707d}}.trend-name{{font-size:16px;font-weight:900;margin:5px 0}}.report-panel{{display:flex;justify-content:space-between;align-items:center;margin-top:18px;border-color:rgba(255,90,20,.35)}}
.stDownloadButton>button{{background:linear-gradient(90deg,{RED},{ORANGE});color:#fff;border:0;font-weight:800}}
</style>''',unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f'<div class="brand"><div class="brand-title">Petro<span>AI</span></div><div class="brand-sub">Petroleum Production Expert System</div></div>',unsafe_allow_html=True)
    page=st.radio('MAIN MODULES',['Dashboard','Data Analysis','Production Trend','Water Cut & WOR','Risk Assessment','Expert Analysis','PDF Report'])
    st.markdown('### FIELD ASSETS')
    st.markdown('<div class="asset">🏗️ Offshore Rig</div><div class="asset">⬆️ SRP</div><div class="asset">🏭 Production Facility</div><div class="asset">🔩 Wellhead</div>',unsafe_allow_html=True)
    st.caption('PetroAI Analyzer v1.0')

st.markdown('<div class="hero"><div class="hero-inner"><div>🔥 Welcome to</div><h1>Petro<span>AI</span> Analyzer</h1><p>Analyze well production performance, identify water-related risks, and get petroleum engineering recommendations from production data.</p><div class="tag">Smarter Analysis. Better Decisions. Higher Production.</div><div><span class="asset">🏗️ Offshore Rig</span><span class="asset">⬆️ SRP</span><span class="asset">🏭 Production Facility</span><span class="asset">🔩 Wellhead</span></div></div></div>',unsafe_allow_html=True)

with st.expander('📁 Upload Production Data',expanded=True):
    uploaded=st.file_uploader('Excel / CSV',type=['xlsx','csv'])

if uploaded is None:
    st.markdown('<div class="panel"><h3>🚀 Ready for Production Analysis</h3><p>Upload Excel/CSV untuk mengaktifkan semua modul PetroAI.</p></div>',unsafe_allow_html=True)
    st.info('Kolom wajib: Date, Oil Rate, Water Rate')
    st.stop()

try:
    df=pd.read_excel(uploaded) if uploaded.name.lower().endswith('xlsx') else pd.read_csv(uploaded)
    req=['Date','Oil Rate','Water Rate']; miss=[x for x in req if x not in df.columns]
    if miss: raise ValueError('Kolom belum ditemukan: '+', '.join(miss))
    df['Date']=pd.to_datetime(df['Date'],errors='coerce'); df['Oil Rate']=pd.to_numeric(df['Oil Rate'],errors='coerce'); df['Water Rate']=pd.to_numeric(df['Water Rate'],errors='coerce')
    df=df.dropna(subset=req).sort_values('Date').reset_index(drop=True)
    if df.empty: raise ValueError('Tidak ada data valid.')
    df['Total Fluid']=df['Oil Rate']+df['Water Rate']; df['Water Cut (%)']=df.apply(lambda r:r['Water Rate']/r['Total Fluid']*100 if r['Total Fluid'] else 0,axis=1); df['WOR']=df.apply(lambda r:r['Water Rate']/r['Oil Rate'] if r['Oil Rate'] else None,axis=1)
except Exception as e:
    st.error('❌ '+str(e)); st.stop()

def trend(s):
    v=pd.Series(s).dropna().reset_index(drop=True)
    if len(v)<2:return 0,'Data tidak cukup'
    x=pd.Series(range(len(v))); den=((x-x.mean())**2).sum(); slope=((x-x.mean())*(v-v.mean())).sum()/den; n=slope/v.mean()*100 if v.mean() else 0
    return n,'Meningkat' if n>.10 else 'Menurun' if n<-.10 else 'Relatif Stabil'

oil_slope,oil_trend=trend(df['Oil Rate']); water_slope,water_trend=trend(df['Water Rate']); wc_slope,wc_trend=trend(df['Water Cut (%)']); wor_slope,wor_trend=trend(df['WOR'])
first,last=df.iloc[0],df.iloc[-1]
oil_change=(last['Oil Rate']-first['Oil Rate'])/first['Oil Rate']*100 if first['Oil Rate'] else 0; wc_change=last['Water Cut (%)']-first['Water Cut (%)']; wor_change=(last['WOR']-first['WOR'])/first['WOR']*100 if pd.notna(first['WOR']) and first['WOR'] else 0
score=100
if oil_change<-20:score-=30
elif oil_change<-10:score-=20
elif oil_change<0:score-=10
if wc_change>10:score-=25
elif wc_change>5:score-=15
elif wc_change>0:score-=5
if wor_change>50:score-=25
elif wor_change>20:score-=15
elif wor_change>0:score-=5
if last['Water Cut (%)']>=90:score-=15
elif last['Water Cut (%)']>=80:score-=10
score=max(0,min(100,score)); status='GOOD' if score>=80 else 'MONITOR' if score>=60 else 'ATTENTION' if score>=40 else 'CRITICAL'

risk=0; reasons=[]
for tr,pts,text in [(oil_trend,2,'Oil Rate menurun.'),(water_trend,2,'Water Rate meningkat.'),(wc_trend,2,'Water Cut meningkat.'),(wor_trend,2,'WOR meningkat.')]:
    if (tr=='Menurun' and text.startswith('Oil')) or (tr=='Meningkat' and not text.startswith('Oil')):risk+=pts;reasons.append(text)
if last['Water Cut (%)']>=90:risk+=3;reasons.append(f"Water Cut akhir {last['Water Cut (%)']:.1f}%.")
elif last['Water Cut (%)']>=80:risk+=2;reasons.append(f"Water Cut akhir {last['Water Cut (%)']:.1f}%.")
elif last['Water Cut (%)']>=70:risk+=1;reasons.append(f"Water Cut akhir {last['Water Cut (%)']:.1f}%.")
risk_level='LOW RISK' if risk<=2 else 'MEDIUM RISK' if risk<=5 else 'HIGH RISK' if risk<=8 else 'CRITICAL RISK'

if oil_trend=='Menurun' and wc_trend=='Meningkat' and wor_trend=='Meningkat':
    rec_title='Indikasi penurunan performa dan peningkatan kontribusi air'; rec_text='Oil Rate menurun sementara Water Cut dan WOR meningkat.'; actions=['Evaluasi well test berikutnya.','Periksa performa artificial lift/ESP bila digunakan.','Evaluasi perubahan Water Rate dan kemungkinan sumber air.','Bandingkan dengan well test periode sebelumnya.','Jika tersedia, lanjutkan evaluasi reservoir.']
elif oil_trend=='Menurun' and water_trend=='Meningkat':
    rec_title='Penurunan Oil Rate dengan peningkatan Water Rate'; rec_text='Produksi minyak cenderung turun sementara produksi air meningkat.'; actions=['Monitor Water Cut dan WOR.','Evaluasi well test berkala.','Periksa artificial lift jika tersedia.','Bandingkan laju minyak dan air antar-periode.']
elif wc_trend=='Meningkat' or wor_trend=='Meningkat':
    rec_title='Peningkatan kontribusi air'; rec_text='Water Cut atau WOR menunjukkan tren meningkat.'; actions=['Monitor Water Cut dan WOR.','Evaluasi perkembangan Water Rate.','Identifikasi perubahan mendadak vs bertahap.','Evaluasi artificial lift jika produksi berubah signifikan.']
elif oil_trend=='Meningkat' and wc_trend!='Meningkat' and wor_trend!='Meningkat':
    rec_title='Performa produksi relatif positif'; rec_text='Oil Rate meningkat tanpa peningkatan signifikan pada Water Cut maupun WOR.'; actions=['Pertahankan monitoring produksi.','Monitor Water Cut dan WOR.','Evaluasi kestabilan artificial lift.']
else:
    rec_title='Performa produksi memerlukan monitoring'; rec_text='Belum ada kombinasi perubahan parameter yang menunjukkan kondisi ekstrem.'; actions=['Monitoring rutin parameter produksi.','Bandingkan hasil well test antar-periode.','Perhatikan perubahan Water Cut dan WOR.']

def make_pdf_report():
    b=BytesIO();doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=1.5*cm,leftMargin=1.5*cm,topMargin=1.5*cm,bottomMargin=1.5*cm);styles=getSampleStyleSheet();h=ParagraphStyle('h2x',parent=styles['Heading2'],textColor=colors.HexColor('#d62b1f'),spaceBefore=10,spaceAfter=6);story=[Paragraph('PetroAI Analyzer',styles['Title']),Paragraph('Petroleum Production Expert System',styles['Heading3']),Spacer(1,.3*cm),Paragraph('1. Production Summary',h)]
    data=[['Parameter','Average'],['Oil Rate',f"{df['Oil Rate'].mean():.2f}"],['Water Rate',f"{df['Water Rate'].mean():.2f}"],['Water Cut',f"{df['Water Cut (%)'].mean():.2f}%"],['WOR',f"{df.WOR.mean():.2f}"]];t=Table(data,colWidths=[7*cm,7*cm]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),6)]));story += [t,Paragraph('2. Performance Score',h),Paragraph(f'{score}/100 — {status}',styles['BodyText']),Paragraph('3. Trend Analysis',h)]
    for n,tr,s in [('Oil Rate',oil_trend,oil_slope),('Water Rate',water_trend,water_slope),('Water Cut',wc_trend,wc_slope),('WOR',wor_trend,wor_slope)]: story.append(Paragraph(f'{n}: {tr} ({s:.3f}%)',styles['BodyText']))
    story += [Paragraph('4. Risk Assessment',h),Paragraph(f'{risk}/11 — {risk_level}',styles['BodyText']),Paragraph('5. Engineering Recommendation',h),Paragraph(f'<b>{rec_title}</b>',styles['BodyText']),Paragraph(rec_text,styles['BodyText'])]
    for x in actions: story.append(Paragraph('• '+x,styles['BodyText']))
    story.append(PageBreak());story.append(Paragraph('6. Production Charts',h))
    for col in ['Oil Rate','Water Rate','Water Cut (%)','WOR']:
        fig,ax=plt.subplots(figsize=(7.2,3.5));ax.plot(df.Date,df[col],marker='o');ax.set_title(col+' vs Time');ax.set_xlabel('Date');ax.set_ylabel(col);ax.grid(True,alpha=.3);fig.autofmt_xdate();ib=BytesIO();fig.savefig(ib,format='png',dpi=150,bbox_inches='tight');plt.close(fig);ib.seek(0);story += [Image(ib,width=17*cm,height=8*cm),Spacer(1,.2*cm)]
    doc.build(story);b.seek(0);return b

# ---------------- PAGES ----------------
if page=='Dashboard':
    st.success(f'✅ {uploaded.name} berhasil dibaca • {len(df)} data points')
    k=st.columns(4)
    vals=[('AVERAGE OIL RATE',f"{df['Oil Rate'].mean():,.2f}",'production rate',False),('AVERAGE WATER CUT',f"{df['Water Cut (%)'].mean():.2f}%",f"latest {last['Water Cut (%)']:.2f}%",True),('AVERAGE WOR',f"{df['WOR'].mean():.2f}",'water / oil ratio',False),('PRODUCTION HEALTH',f'{score}/100',status,True)]
    for c,(lab,val,note,orange) in zip(k,vals):c.markdown(f'<div class="card {"orange" if orange else ""}"><div class="label">{lab}</div><div class="value">{val}</div><div class="note">{note}</div></div>',unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        fig=go.Figure();fig.add_trace(go.Scatter(x=df.Date,y=df['Oil Rate'],mode='lines+markers',name='Oil Rate',line=dict(color=RED,width=3)));fig.add_trace(go.Scatter(x=df.Date,y=df['Water Rate'],mode='lines+markers',name='Water Rate',line=dict(color=ORANGE,width=3)));fig.update_layout(template='plotly_dark',height=360,title='Production Trend',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)');st.plotly_chart(fig,use_container_width=True)
    with c2:
        fig=go.Figure();fig.add_trace(go.Scatter(x=df.Date,y=df['Water Cut (%)'],mode='lines+markers',name='Water Cut',line=dict(color=RED,width=3)));fig.add_trace(go.Scatter(x=df.Date,y=df.WOR,mode='lines+markers',name='WOR',yaxis='y2',line=dict(color=ORANGE,width=3)));fig.update_layout(template='plotly_dark',height=360,title='Water Cut & WOR',yaxis=dict(title='Water Cut (%)'),yaxis2=dict(title='WOR',overlaying='y',side='right'),paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)');st.plotly_chart(fig,use_container_width=True)
    # Full dashboard continuation
    st.markdown('<div class="section-title">⛽ Well Performance & Risk Overview</div>',unsafe_allow_html=True)
    left,mid,right=st.columns([1.45,1,1.15])
    with left:
        st.markdown('<div class="panel"><h3>🛢️ Well Performance</h3><p>Current production condition based on the uploaded dataset.</p></div>',unsafe_allow_html=True)
        show=df[['Date','Oil Rate','Water Rate','Water Cut (%)','WOR']].copy()
        show['Date']=show['Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(show,use_container_width=True,hide_index=True,height=250)
    with mid:
        st.markdown('<div class="panel"><h3>🚨 Risk Assessment</h3></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="risk-score"><div class="risk-number">{risk}</div><div>/ 11</div></div><div class="risk-badge">{risk_level}</div>',unsafe_allow_html=True)
        if reasons:
            for r in reasons: st.markdown(f'<div class="mini-risk">⚠️ {r}</div>',unsafe_allow_html=True)
        else: st.markdown('<div class="mini-risk">✓ No major risk factor detected</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="panel"><h3>🧠 Expert Analysis</h3></div>',unsafe_allow_html=True)
        st.markdown(f'<div class="finding"><b>Key Finding</b><br>{rec_title}</div>',unsafe_allow_html=True)
        st.markdown(f'<div class="finding"><b>Interpretation</b><br>{rec_text}</div>',unsafe_allow_html=True)
        for a in actions[:4]: st.markdown(f'<div class="action">✓ {a}</div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">📊 Production Data Summary</div>',unsafe_allow_html=True)
    s1,s2,s3,s4=st.columns(4)
    summary=[('Oil Rate Change',f'{oil_change:+.2f}%','First → Last'),('Water Cut Change',f'{wc_change:+.2f} pp','First → Last'),('WOR Change',f'{wor_change:+.2f}%','First → Last'),('Analysis Period',f'{(last["Date"]-first["Date"]).days} days','Data coverage')]
    for c,(a,b,d) in zip([s1,s2,s3,s4],summary): c.markdown(f'<div class="card orange"><div class="label">{a}</div><div class="value">{b}</div><div class="note">{d}</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="section-title">📈 Trend Diagnostics</div>',unsafe_allow_html=True)
    t1,t2,t3,t4=st.columns(4)
    trends=[('Oil Rate',oil_trend,oil_slope),('Water Rate',water_trend,water_slope),('Water Cut',wc_trend,wc_slope),('WOR',wor_trend,wor_slope)]
    for c,(name,tr,sl) in zip([t1,t2,t3,t4],trends):
        cls='trend-bad' if ((name=='Oil Rate' and tr=='Menurun') or (name!='Oil Rate' and tr=='Meningkat')) else 'trend-good' if ((name=='Oil Rate' and tr=='Meningkat') or (name!='Oil Rate' and tr=='Menurun')) else 'trend-neutral'
        c.markdown(f'<div class="trend-card {cls}"><div class="label">{name}</div><div class="trend-name">{tr}</div><div class="note">Normalized slope {sl:.3f}%</div></div>',unsafe_allow_html=True)

    st.markdown('<div class="panel report-panel"><div><h3>📄 PetroAI Engineering Report</h3><p>Generate a complete PDF containing production summary, trend diagnostics, risk assessment, engineering recommendations, and charts.</p></div></div>',unsafe_allow_html=True)
    if st.button('🔥 Generate PDF Report',key='dashboard_pdf',use_container_width=True):
        try:
            pdf=make_pdf_report()
            st.success('✅ PDF report berhasil dibuat!')
            st.download_button('⬇️ Download PetroAI Engineering Report',pdf.getvalue(),'PetroAI_Engineering_Report.pdf','application/pdf',use_container_width=True,key='dashboard_pdf_download')
        except Exception as e: st.error('❌ '+str(e))

    st.markdown(f'<div class="finding"><b>🧠 Expert Summary:</b> {rec_title}. {rec_text}</div>',unsafe_allow_html=True)

elif page=='Data Analysis':
    st.markdown('<div class="panel"><h3>📊 Data Analysis</h3><p>Calculated production parameters.</p></div>',unsafe_allow_html=True);st.dataframe(df,use_container_width=True,hide_index=True);st.download_button('⬇️ Download Calculated CSV',df.to_csv(index=False).encode(), 'PetroAI_Calculated_Data.csv','text/csv')

elif page=='Production Trend':
    st.markdown('<div class="panel"><h3>📈 Production Trend</h3><p>Normalized linear-regression trend classification.</p></div>',unsafe_allow_html=True)
    for name,col,slope,tr in [('Oil Rate','Oil Rate',oil_slope,oil_trend),('Water Rate','Water Rate',water_slope,water_trend),('Water Cut','Water Cut (%)',wc_slope,wc_trend),('WOR','WOR',wor_slope,wor_trend)]:
        st.markdown(f'<div class="finding"><b>{name}</b> — {tr} — normalized slope {slope:.3f}%</div>',unsafe_allow_html=True)
    for col in ['Oil Rate','Water Rate']:
        fig=go.Figure(go.Scatter(x=df.Date,y=df[col],mode='lines+markers',line=dict(color=RED if col=='Oil Rate' else ORANGE,width=3)));fig.update_layout(template='plotly_dark',height=350,title=col+' vs Time',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)');st.plotly_chart(fig,use_container_width=True)

elif page=='Water Cut & WOR':
    c1,c2=st.columns(2)
    for c,col,title,color in [(c1,'Water Cut (%)','Water Cut vs Time',RED),(c2,'WOR','WOR vs Time',ORANGE)]:
        with c:
            fig=go.Figure(go.Scatter(x=df.Date,y=df[col],mode='lines+markers',line=dict(color=color,width=3)));fig.update_layout(template='plotly_dark',height=390,title=title,paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)');st.plotly_chart(fig,use_container_width=True)
    st.markdown(f'<div class="finding"><b>Interpretasi:</b> Water Cut terakhir {last["Water Cut (%)"]:.2f}% • rata-rata {df["Water Cut (%)"].mean():.2f}% • WOR rata-rata {df.WOR.mean():.2f}. Trend: WC <b>{wc_trend}</b>, WOR <b>{wor_trend}</b>.</div>',unsafe_allow_html=True)

elif page=='Risk Assessment':
    st.markdown(f'<div class="panel"><h3>🚨 Risk Assessment</h3><div class="value">{risk}/11</div><div class="finding"><b>{risk_level}</b></div></div>',unsafe_allow_html=True)
    if reasons:
        for r in reasons:st.write('⚠️',r)
    else:st.success('Tidak ditemukan risk factor utama.')

elif page=='Expert Analysis':
    water_change=(last['Water Rate']-first['Water Rate'])/first['Water Rate']*100 if first['Water Rate'] else 0
    items=[('Oil Rate',f"{oil_change:+.2f}% dari data awal ke akhir."),('Water Rate',f"{water_change:+.2f}% dari data awal ke akhir."),('Water Cut',f"{wc_change:+.2f} percentage point."),('WOR',f"{wor_change:+.2f}% dari data awal ke akhir.")]
    for t,x in items:st.markdown(f'<div class="finding"><b>{t}</b><br>{x}</div>',unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><h3>🛠️ Engineering Recommendation</h3><div class="finding"><b>{rec_title}</b><br>{rec_text}</div></div>',unsafe_allow_html=True)
    for x in actions:st.write('✓',x)

else:
    st.markdown('<div class="panel"><h3>📄 PDF Engineering Report</h3><p>Summary + trend + risk + recommendation + charts.</p></div>',unsafe_allow_html=True)
    def make_pdf():
        b=BytesIO();doc=SimpleDocTemplate(b,pagesize=A4,rightMargin=1.5*cm,leftMargin=1.5*cm,topMargin=1.5*cm,bottomMargin=1.5*cm);styles=getSampleStyleSheet();h=ParagraphStyle('h',parent=styles['Heading2'],textColor=colors.HexColor('#d62b1f'),spaceBefore=10,spaceAfter=6);story=[Paragraph('PetroAI Analyzer',styles['Title']),Paragraph('Petroleum Production Expert System',styles['Heading3']),Spacer(1,.3*cm),Paragraph('1. Production Summary',h)]
        data=[['Parameter','Average'],['Oil Rate',f"{df['Oil Rate'].mean():.2f}"],['Water Rate',f"{df['Water Rate'].mean():.2f}"],['Water Cut',f"{df['Water Cut (%)'].mean():.2f}%"],['WOR',f"{df.WOR.mean():.2f}"]];t=Table(data,colWidths=[7*cm,7*cm]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.lightgrey),('GRID',(0,0),(-1,-1),.5,colors.grey),('PADDING',(0,0),(-1,-1),6)]));story+=[t,Paragraph('2. Performance Score',h),Paragraph(f'{score}/100 — {status}',styles['BodyText']),Paragraph('3. Trend Analysis',h)]
        for n,tr,s in [('Oil Rate',oil_trend,oil_slope),('Water Rate',water_trend,water_slope),('Water Cut',wc_trend,wc_slope),('WOR',wor_trend,wor_slope)]:story.append(Paragraph(f'{n}: {tr} ({s:.3f}%)',styles['BodyText']))
        story += [Paragraph('4. Risk Assessment',h),Paragraph(f'{risk}/11 — {risk_level}',styles['BodyText']),Paragraph('5. Engineering Recommendation',h),Paragraph(f'<b>{rec_title}</b>',styles['BodyText']),Paragraph(rec_text,styles['BodyText'])]
        for x in actions:story.append(Paragraph('• '+x,styles['BodyText']))
        story.append(PageBreak());story.append(Paragraph('6. Production Charts',h))
        for col in ['Oil Rate','Water Rate','Water Cut (%)','WOR']:
            fig,ax=plt.subplots(figsize=(7.2,3.5));ax.plot(df.Date,df[col],marker='o');ax.set_title(col+' vs Time');ax.set_xlabel('Date');ax.set_ylabel(col);ax.grid(True,alpha=.3);fig.autofmt_xdate();ib=BytesIO();fig.savefig(ib,format='png',dpi=150,bbox_inches='tight');plt.close(fig);ib.seek(0);story += [Image(ib,width=17*cm,height=8*cm),Spacer(1,.2*cm)]
        doc.build(story);b.seek(0);return b
    if st.button('🔥 Generate PDF Report',use_container_width=True):
        try:
            pdf=make_pdf_report();st.success('✅ PDF report berhasil dibuat!');st.download_button('⬇️ Download PetroAI Engineering Report',pdf.getvalue(),'PetroAI_Engineering_Report.pdf','application/pdf',use_container_width=True)
        except Exception as e:st.error('❌ '+str(e))

st.markdown('<div class="footer">PetroAI • Petroleum Production Analytics • Rule-Based Expert System • From Data to Better Production</div>',unsafe_allow_html=True)
