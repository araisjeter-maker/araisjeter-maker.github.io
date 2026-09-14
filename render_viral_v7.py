import argparse, subprocess, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=720,1280,30
ROOT=Path(__file__).parent
A=ROOT/'assets_v7'; O=ROOT/'overlays_v7'; P=ROOT/'parts_v7'; V=ROOT/'videos'; PRE=ROOT/'previews_v7'
for d in (A,O,P,V,PRE): d.mkdir(exist_ok=True)
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
WHITE=(255,255,255,255); INK=(28,21,31,255); LILAC=(190,132,211,255)
CORAL=(255,108,120,255); CREAM=(255,247,231,255); MINT=(160,228,209,255); YELLOW=(255,214,88,255)

# Todos os clipes são novos, gratuitos e diferentes dos usados nos vídeos anteriores.
SRC={
 'm_chew':'https://www.pexels.com/download/video/4196229/',
 'm_key':'https://www.pexels.com/download/video/5647324/',
 'm_clock':'https://www.pexels.com/download/video/7033786/',
 'm_coffee':'https://www.pexels.com/download/video/17422066/',
 'm_key2':'https://www.pexels.com/download/video/7581246/',
 'd_calc':'https://www.pexels.com/download/video/7688135/',
 'd_receipt':'https://www.pexels.com/download/video/5981287/',
 'd_coins':'https://www.pexels.com/download/video/35996682/',
 'd_measure':'https://www.pexels.com/download/video/8004761/',
 'd_bus':'https://www.pexels.com/download/video/36138611/',
 'd_clock':'https://www.pexels.com/download/video/9160919/'
}

def run(c):
 print(' '.join(map(str,c)),flush=True); subprocess.run(c,check=True)

def download(k):
 out=A/f'{k}.mp4'
 if out.exists() and out.stat().st_size>100000:return out
 page=SRC[k]
 run(['curl','-L','--fail','--retry','3','--connect-timeout','10','--max-time','240',
      '-A','Mozilla/5.0','-o',str(out),page])
 if not out.exists() or out.stat().st_size<100000: raise RuntimeError('Falha na fonte gratuita: '+k)
 return out

def font(n,b=True): return ImageFont.truetype(B if b else R,n)
def tw(d,t,f): return d.textbbox((0,0),t,font=f)[2]
def wrap(d,t,f,maxw):
 out=[]; cur=''
 for word in t.split():
  test=(cur+' '+word).strip()
  if cur and tw(d,test,f)>maxw: out.append(cur); cur=word
  else: cur=test
 if cur: out.append(cur)
 return out

def lines(d,text,y,f,fill,maxw=620,center=True,x=50,spacing=8,shadow=True):
 arr=wrap(d,text,f,maxw)
 for line in arr:
  xx=(W-tw(d,line,f))//2 if center else x
  if shadow:d.text((xx+3,y+4),line,font=f,fill=(0,0,0,165))
  d.text((xx,y),line,font=f,fill=fill)
  y+=f.size+spacing
 return y

def miso_overlay(path,b):
 im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
 mode=b['mode']; text=b['text']
 # identidade de suspense: imagem cheia, faixa mínima e cortes agressivos
 d.rounded_rectangle((25,26,190,66),18,fill=(22,16,25,215))
 d.ellipse((42,40,54,52),fill=CORAL)
 d.text((66,37),'SOM DESLIGADO',font=font(13,False),fill=WHITE)
 if mode=='hook':
  d.rectangle((0,0,W,H),fill=(10,6,12,55))
  lines(d,text,470,font(b.get('size',62)),WHITE,650)
 elif mode=='trigger':
  d.rounded_rectangle((42,900,678,1045),26,fill=(24,17,28,218))
  d.text((70,923),b.get('tag','VOCÊ ANTECIPOU O SOM?'),font=font(15,False),fill=LILAC)
  lines(d,text,962,font(b.get('size',35)),WHITE,570,center=False,x=70,spacing=5)
 elif mode=='truth':
  d.rectangle((0,760,W,1135),fill=(22,15,26,205))
  d.rectangle((0,760,12,1135),fill=CORAL)
  lines(d,text,820,font(b.get('size',39)),WHITE,620,center=False,x=44)
 elif mode=='word':
  d.rectangle((0,0,W,H),fill=(27,16,31,155))
  d.text((50,390),'ISSO TEM NOME:',font=font(20,False),fill=(228,198,238,255))
  lines(d,text,455,font(76),WHITE,630,center=False,x=50)
  d.rectangle((50,570,440,579),fill=CORAL)
 elif mode=='final':
  d.rectangle((0,0,W,H),fill=(24,14,29,195))
  lines(d,text,285,font(51),WHITE,630)
  d.rounded_rectangle((45,800,675,980),28,fill=(246,228,250,245))
  lines(d,b['small'],842,font(27),INK,555,shadow=False)
 d.text((30,1218),'@fealemdodiagnostico',font=font(15,False),fill=WHITE)
 im.save(path)

def dys_overlay(path,b):
 im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
 mode=b['mode']; text=b['text']
 # identidade documental: etiquetas editoriais laterais e números em destaque
 d.rectangle((28,30,36,112),fill=YELLOW)
 d.text((50,38),'UM DIA ENTRE NÚMEROS',font=font(15,False),fill=WHITE)
 if mode=='hook':
  d.polygon([(0,770),(720,700),(720,1120),(0,1190)],fill=(20,28,31,218))
  lines(d,text,805,font(b.get('size',56)),WHITE,625,center=False,x=48)
 elif mode=='scene':
  d.rounded_rectangle((42,160,250,205),20,fill=(16,24,27,220))
  d.text((66,172),b['tag'],font=font(14,False),fill=MINT)
  d.rounded_rectangle((42,845,678,1055),24,fill=(255,247,231,238))
  lines(d,text,885,font(b.get('size',42)),INK,570,center=False,x=72,shadow=False)
  if b.get('number'):
   f=font(74); n=b['number']; x=72
   d.text((x,700),n,font=f,fill=YELLOW,stroke_width=3,stroke_fill=(30,27,25,255))
 elif mode=='fact':
  d.rectangle((0,810,W,1135),fill=(246,239,220,235))
  d.rectangle((0,810,14,1135),fill=MINT)
  d.text((44,842),b.get('tag','O QUE QUASE NINGUÉM VÊ'),font=font(15,False),fill=(54,113,99,255))
  lines(d,text,892,font(b.get('size',35)),INK,610,center=False,x=44,shadow=False)
 elif mode=='name':
  d.rectangle((0,0,W,H),fill=(15,27,28,165))
  d.text((48,360),'NÃO É “FALTA DE ATENÇÃO”.',font=font(21,False),fill=MINT)
  lines(d,text,430,font(66),WHITE,620,center=False,x=48)
  d.rectangle((48,610,570,620),fill=YELLOW)
 elif mode=='final':
  d.rectangle((0,0,W,H),fill=(15,27,28,205))
  d.text((48,205),'COMENTE UMA OPÇÃO:',font=font(20,False),fill=MINT)
  lines(d,text,285,font(48),WHITE,620,center=False,x=48)
  d.rounded_rectangle((48,790,672,965),24,fill=(255,247,231,245))
  lines(d,b['small'],830,font(27),INK,555,shadow=False)
 d.text((30,1218),'@fealemdodiagnostico',font=font(15,False),fill=WHITE)
 im.save(path)

MISO=[
 {'src':'m_clock','mode':'hook','text':'ESTE VÍDEO ESTÁ MUDO.','dur':1.1,'start':0},
 {'src':'m_chew','mode':'hook','text':'ENTÃO POR QUE SEU CORPO REAGIU?','dur':1.3,'start':0,'size':48},
 {'src':'m_key','mode':'hook','text':'SÓ DE VER ISTO...','dur':1.4,'start':1},
 {'src':'m_chew','mode':'trigger','tag':'SEM SOM','text':'Você antecipou a mastigação?','dur':2.5,'start':2},
 {'src':'m_key2','mode':'trigger','tag':'SEM SOM','text':'E o teclado?','dur':2.5,'start':1},
 {'src':'m_clock','mode':'trigger','tag':'SEM SOM','text':'E o tique-taque?','dur':2.5,'start':4},
 {'src':'m_coffee','mode':'truth','text':'Para algumas pessoas, não é um simples incômodo.','dur':3.2,'start':0},
 {'src':'m_clock','mode':'truth','text':'O corpo entra em alerta antes de dar tempo de explicar.','dur':3.2,'start':7},
 {'src':'m_key','mode':'truth','text':'Raiva. Angústia. Urgência de sair.','dur':3.2,'start':5},
 {'src':'m_chew','mode':'word','text':'MISOFONIA','dur':3.3,'start':5},
 {'src':'m_clock','mode':'truth','text':'A reação depende do padrão ou do significado do som — não só do volume.','dur':3.5,'start':10,'size':34},
 {'src':'m_key2','mode':'truth','text':'Mastigar. Teclar. Clicar. Tique-taque.','dur':3.2,'start':6},
 {'src':'m_chew','mode':'truth','text':'Às vezes, até ver o movimento associado já causa sofrimento.','dur':3.4,'start':8,'size':35},
 {'src':'m_coffee','mode':'truth','text':'Não é escolha. Não é “frescura”.','dur':3.3,'start':4},
 {'src':'m_key','mode':'truth','text':'E não significa que a pessoa odeia você.','dur':3.3,'start':9},
 {'src':'m_clock','mode':'truth','text':'Amor também é permitir distância, pausa ou proteção.','dur':3.4,'start':13},
 {'src':'m_coffee','mode':'truth','text':'Este vídeo não é diagnóstico.','dur':3.0,'start':8},
 {'src':'m_key2','mode':'truth','text':'Mas talvez dê nome a um sofrimento invisível.','dur':3.4,'start':11},
 {'src':'m_clock','mode':'final','text':'QUAL SOM FAZ SEU CORPO ENTRAR EM ALERTA?','small':'Compartilhe para trocar julgamento por acolhimento.','dur':6.0,'start':16}
]

DYS=[
 {'src':'d_calc','mode':'hook','text':'ELA NÃO ERROU A CONTA.','dur':1.2,'start':0},
 {'src':'d_receipt','mode':'hook','text':'O NÚMERO MUDOU DE LUGAR.','dur':1.4,'start':0},
 {'src':'d_clock','mode':'hook','text':'ACOMPANHE UM DIA...','dur':1.4,'start':0},
 {'src':'d_clock','mode':'scene','tag':'07:45 • ACORDAR','number':'07:45','text':'Ou era 07:54?','dur':3.0,'start':2},
 {'src':'d_bus','mode':'scene','tag':'08:30 • ROTA','number':'174','text':'O ônibus era 174 ou 147?','dur':3.0,'start':0},
 {'src':'d_receipt','mode':'scene','tag':'12:10 • PAGAR','number':'68,90','text':'R$ 68,90 ou R$ 86,90?','dur':3.2,'start':3},
 {'src':'d_coins','mode':'scene','tag':'12:12 • TROCO','number':'7,50','text':'O troco está certo?','dur':3.2,'start':1},
 {'src':'d_measure','mode':'scene','tag':'19:05 • RECEITA','number':'1/2','text':'Meia xícara ou duas?','dur':3.2,'start':2},
 {'src':'d_calc','mode':'fact','text':'Para algumas pessoas, isso não é distração.','dur':3.0,'start':4},
 {'src':'d_bus','mode':'fact','text':'É esforço diário para lidar com quantidades, sequência, tempo e cálculo.','dur':3.0,'start':4,'size':33},
 {'src':'d_coins','mode':'name','text':'DISCALCULIA','dur':3.0,'start':5},
 {'src':'d_receipt','mode':'fact','text':'É uma dificuldade persistente em compreender e trabalhar com números.','dur':3.0,'start':7,'size':33},
 {'src':'d_clock','mode':'fact','text':'Pode aparecer no relógio, no dinheiro, nas medidas e no cálculo mental.','dur':3.0,'start':7,'size':33},
 {'src':'d_calc','mode':'fact','text':'Não mede inteligência.','dur':3.0,'start':8},
 {'src':'d_receipt','mode':'fact','text':'Nem se resolve com “presta atenção”.','dur':3.0,'start':10},
 {'src':'d_coins','mode':'fact','text':'Pressa e vergonha podem roubar ainda mais clareza.','dur':3.0,'start':9},
 {'src':'d_measure','mode':'fact','text':'Apoio visual, calculadora e tempo extra podem devolver autonomia.','dur':3.0,'start':8,'size':33},
 {'src':'d_bus','mode':'fact','text':'Deus não mede ninguém pela rapidez de uma conta.','dur':3.4,'start':9},
 {'src':'d_clock','mode':'fact','text':'Este vídeo não é um teste diagnóstico.','dur':3.4,'start':11},
 {'src':'d_calc','mode':'final','text':'TEMPO • TROCO • MEDIDAS • ROTAS','small':'Qual deles mais complica o seu dia?','dur':5.6,'start':12}
]

def render_scene(src,ov,out,dur,start,style,i):
 if style=='miso':
  grade='eq=contrast=1.24:saturation=.72:brightness=-.02,unsharp=5:5:.55'
  motion=f"scale=790:1405,crop=720:1280:x='35+18*sin(t*1.6+{i})':y='62+13*cos(t*1.3)'"
 else:
  grade='eq=contrast=1.10:saturation=.92:brightness=.02,colorbalance=gs=.015:bs=.02'
  motion=f"scale=760:1352,crop=720:1280:x='20+8*sin(t*.55+{i})':y='36+7*cos(t*.5)'"
 filt=f"[0:v]{motion},fps={FPS},{grade},format=yuv420p[bg];[1:v]format=rgba,fade=t=in:st=0:d=0.08:alpha=1,fade=t=out:st={max(0.1,dur-0.10)}:d=0.10:alpha=1[ov];[bg][ov]overlay=0:0:format=auto[v]"
 run(['ffmpeg','-y','-loglevel','error','-stream_loop','-1','-ss',str(start),'-i',str(src),'-loop','1','-i',str(ov),'-t',str(dur),'-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(out)])

def build(name,style,beats,preview):
 parts=[]; frames=[]
 for i,b in enumerate(beats):
  src=download(b['src']); ov=O/f'{name}_{i:02}.png'; part=P/f'{name}_{i:02}.mp4'
  (miso_overlay if style=='miso' else dys_overlay)(ov,b)
  render_scene(src,ov,part,b['dur'],b.get('start',0),style,i); parts.append(part)
  shot=PRE/f'{name}_{i:02}.jpg'
  run(['ffmpeg','-y','-loglevel','error','-ss',str(b['dur']/2),'-i',str(part),'-frames:v','1',str(shot)]); frames.append(shot)
 thumbs=[]
 for f in frames:
  im=Image.open(f).convert('RGB'); im.thumbnail((180,320)); thumbs.append(im.copy())
 sheet=Image.new('RGB',(900,((len(thumbs)+4)//5)*320),(20,15,22))
 for i,im in enumerate(thumbs): sheet.paste(im,((i%5)*180,(i//5)*320))
 sheet.save(PRE/f'{name}_contato.jpg',quality=88)
 if preview:return
 lst=P/f'{name}.txt'; lst.write_text(''.join(f"file '{p.resolve()}'\n" for p in parts))
 base=P/f'{name}_base.mp4'; out=V/f'{name}.mp4'
 run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',str(base)])
 run(['ffmpeg','-y','-loglevel','error','-i',str(base),'-vf','scale=1080:1920:flags=lanczos','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(out)])
 run(['ffprobe','-v','error','-show_entries','stream=width,height:format=duration,size','-of','default=noprint_wrappers=1',str(out)])

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); x=ap.parse_args()
 build('Video_1_Misofonia_experiencia_silenciosa_v7','miso',MISO,x.preview)
 build('Video_2_Discalculia_um_dia_entre_numeros_v7','dys',DYS,x.preview)
