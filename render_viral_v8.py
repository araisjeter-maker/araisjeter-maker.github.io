import argparse, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=720,1280,30
ROOT=Path(__file__).parent
A=ROOT/'assets_v8'; O=ROOT/'overlays_v8'; P=ROOT/'parts_v8'; V=ROOT/'videos'; PRE=ROOT/'previews_v8'
for d in (A,O,P,V,PRE): d.mkdir(exist_ok=True)
B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
WHITE=(255,255,255,255); LILAC=(204,151,226,255); CORAL=(255,91,112,255)
CYAN=(89,239,226,255); YELLOW=(255,222,85,255); INK=(16,18,23,255)

# Pexels: clipes gratuitos, sem rostos identificáveis e não usados nas versões anteriores.
SRC={
 'm_drip':'https://www.pexels.com/download/video/30615533/',
 'm_type':'https://www.pexels.com/download/video/32388953/',
 'm_paper':'https://www.pexels.com/download/video/7551207/',
 'm_spoon':'https://www.pexels.com/download/video/5526200/',
 'd_pay':'https://www.pexels.com/download/video/6540557/',
 'd_ticket':'https://www.pexels.com/download/video/7252272/',
 'd_atm':'https://www.pexels.com/download/video/5700357/',
 'd_cash':'https://www.pexels.com/download/video/5220466/',
 'd_phone':'https://www.pexels.com/download/video/4121767/',
 'd_card':'https://www.pexels.com/download/video/10224109/'
}

def run(c):
 print(' '.join(map(str,c)),flush=True); subprocess.run(c,check=True)

def download(k):
 out=A/f'{k}.mp4'
 if out.exists() and out.stat().st_size>100000:return out
 run(['curl','-L','--fail','--retry','3','--connect-timeout','10','--max-time','240','-A','Mozilla/5.0','-o',str(out),SRC[k]])
 if not out.exists() or out.stat().st_size<100000: raise RuntimeError('Falha na fonte gratuita: '+k)
 return out

def font(n,b=True): return ImageFont.truetype(B if b else R,n)
def width(d,t,f): return d.textbbox((0,0),t,font=f,stroke_width=0)[2]
def wrap(d,t,f,maxw):
 lines=[]; cur=''
 for word in t.split():
  test=(cur+' '+word).strip()
  if cur and width(d,test,f)>maxw: lines.append(cur); cur=word
  else: cur=test
 if cur:lines.append(cur)
 return lines

def text_lines(d,text,y,f,fill=WHITE,maxw=630,x=None,center=False,spacing=8,stroke=4):
 for line in wrap(d,text,f,maxw):
  xx=(W-width(d,line,f))//2 if center else (x if x is not None else 45)
  d.text((xx,y),line,font=f,fill=fill,stroke_width=stroke,stroke_fill=(0,0,0,190))
  y+=f.size+spacing
 return y

def watermark(d):
 d.text((28,1217),'@fealemdodiagnostico',font=font(15,False),fill=(255,255,255,210),stroke_width=2,stroke_fill=(0,0,0,160))

def miso_overlay(path,b):
 im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
 mode=b['mode']; t=b['text']
 # Sem caixas: tipografia faz parte da cena; marcador editorial mínimo.
 d.line((28,29,692,29),fill=(255,255,255,135),width=2)
 d.line((28,29,28+b.get('progress',80),29),fill=CORAL,width=5)
 if mode=='hook':
  text_lines(d,t,82,font(b.get('size',59)),maxw=650,center=True,spacing=3,stroke=6)
  d.text((W//2-22,1070),'↓',font=font(46),fill=CORAL,stroke_width=2,stroke_fill=(0,0,0,150))
 elif mode=='count':
  n=b['n']; d.text((38,70),n,font=font(164),fill=(255,255,255,72),stroke_width=0)
  text_lines(d,t,950,font(b.get('size',46)),maxw=620,center=True,spacing=2,stroke=6)
 elif mode=='question':
  d.text((53,120),'SEM SOM.',font=font(25),fill=CORAL,stroke_width=3,stroke_fill=(0,0,0,180))
  text_lines(d,t,470,font(b.get('size',57)),maxw=620,center=True,spacing=4,stroke=7)
 elif mode=='reveal':
  d.text((45,96),b.get('eyebrow','O CORPO RESPONDE PRIMEIRO'),font=font(18),fill=LILAC,stroke_width=3,stroke_fill=(0,0,0,170))
  text_lines(d,t,b.get('y',455),font(b.get('size',48)),maxw=620,x=45,spacing=6,stroke=6)
  if b.get('accent'):
   y=b.get('accent_y',770); d.line((48,y,360,y),fill=CORAL,width=9)
 elif mode=='cta':
  text_lines(d,t,210,font(55),maxw=625,center=True,spacing=4,stroke=7)
  d.text((70,890),'1   2   3   4',font=font(66),fill=CORAL,stroke_width=5,stroke_fill=(0,0,0,190))
  text_lines(d,b['small'],1030,font(25),maxw=590,center=True,stroke=4)
 watermark(d); im.save(path)

def dys_overlay(path,b):
 im=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
 mode=b['mode']; t=b['text']
 # Linguagem de microfilme POV: tempo contínuo, números deslocados, sem cards.
 d.text((32,27),b.get('time','08:07'),font=font(18),fill=(255,255,255,210),stroke_width=3,stroke_fill=(0,0,0,170))
 d.line((110,42,690,42),fill=(255,255,255,105),width=2)
 d.ellipse((105+b.get('progress',0),35,119+b.get('progress',0),49),fill=CYAN)
 if mode=='hook':
  d.text((42,120),'POV',font=font(28),fill=CYAN,stroke_width=4,stroke_fill=(0,0,0,190))
  text_lines(d,t,420,font(b.get('size',58)),maxw=630,x=42,spacing=5,stroke=7)
 elif mode=='task':
  d.text((42,115),b['label'],font=font(22),fill=CYAN,stroke_width=3,stroke_fill=(0,0,0,170))
  wrong=b['wrong']; right=b['right']; y=b.get('ny',690)
  d.text((39,y+5),wrong,font=font(98),fill=(255,69,116,210),stroke_width=4,stroke_fill=(0,0,0,170))
  d.text((49,y-3),wrong,font=font(98),fill=(93,237,224,210),stroke_width=3,stroke_fill=(0,0,0,170))
  d.line((46,y+61,655,y+61),fill=YELLOW,width=7)
  d.text((48,y+118),'OU  '+right+'?',font=font(41),fill=WHITE,stroke_width=5,stroke_fill=(0,0,0,190))
  text_lines(d,t,1010,font(27),maxw=620,x=48,spacing=2,stroke=4)
 elif mode=='turn':
  text_lines(d,t,390,font(b.get('size',55)),maxw=630,center=True,spacing=5,stroke=7)
  d.line((120,760,600,760),fill=YELLOW,width=8)
 elif mode=='truth':
  d.text((42,115),b.get('label','O QUE NINGUÉM VÊ'),font=font(20),fill=CYAN,stroke_width=3,stroke_fill=(0,0,0,170))
  text_lines(d,t,b.get('y',530),font(b.get('size',44)),maxw=620,x=42,spacing=7,stroke=6)
 elif mode=='cta':
  d.text((43,130),'QUAL ETAPA TRAVA VOCÊ?',font=font(23),fill=CYAN,stroke_width=3,stroke_fill=(0,0,0,180))
  text_lines(d,t,310,font(52),maxw=625,x=43,spacing=9,stroke=7)
  text_lines(d,b['small'],1010,font(25),maxw=610,x=43,stroke=4)
 watermark(d); im.save(path)

MISO=[
 {'src':'m_drip','mode':'hook','text':'VOCÊ CONSEGUE “OUVIR” ISTO?','dur':1.4,'start':0,'progress':35,'size':54},
 {'src':'m_spoon','mode':'hook','text':'O VÍDEO ESTÁ MUDO.','dur':1.2,'start':1,'progress':50,'size':57},
 {'src':'m_type','mode':'hook','text':'MAS SEU CORPO JÁ ESCOLHEU.','dur':1.4,'start':0,'progress':68,'size':50},
 {'src':'m_drip','mode':'count','n':'1','text':'GOTA REPETINDO','dur':2.6,'start':1,'progress':95},
 {'src':'m_spoon','mode':'count','n':'2','text':'METAL NO PRATO','dur':2.6,'start':2,'progress':120},
 {'src':'m_type','mode':'count','n':'3','text':'TECLAS RÁPIDAS','dur':2.6,'start':2,'progress':145},
 {'src':'m_paper','mode':'count','n':'4','text':'PAPEL AMASSANDO','dur':2.6,'start':1,'progress':170},
 {'src':'m_spoon','mode':'question','text':'QUAL MOVIMENTO FEZ VOCÊ QUERER SAIR?','dur':4.0,'start':5,'progress':215},
 {'src':'m_drip','mode':'reveal','text':'NÃO É PRECISO O SOM COMEÇAR.','dur':4.2,'start':5,'progress':260,'accent':True},
 {'src':'m_type','mode':'reveal','text':'ÀS VEZES, O CÉREBRO JÁ PREVIU O PADRÃO.','dur':4.2,'start':5,'progress':305,'size':43},
 {'src':'m_paper','mode':'reveal','eyebrow':'QUANDO A REAÇÃO É INTENSA','text':'RAIVA. ANGÚSTIA. URGÊNCIA DE FUGIR.','dur':4.4,'start':4,'progress':350,'size':44},
 {'src':'m_spoon','mode':'reveal','eyebrow':'ISSO PODE TER UM NOME','text':'MISOFONIA','dur':4.0,'start':8,'progress':395,'size':72,'accent':True,'accent_y':650},
 {'src':'m_drip','mode':'reveal','text':'NÃO É “FRESCURA”. E NÃO É APENAS VOLUME.','dur':4.4,'start':9,'progress':440,'size':44},
 {'src':'m_type','mode':'reveal','eyebrow':'ACOLHER PODE SER SIMPLES','text':'PAUSA. DISTÂNCIA. PROTEÇÃO.','dur':4.2,'start':9,'progress':485,'size':48},
 {'src':'m_paper','mode':'reveal','eyebrow':'IMPORTANTE','text':'ESTE VÍDEO NÃO É DIAGNÓSTICO.','dur':3.8,'start':8,'progress':530,'size':45},
 {'src':'m_drip','mode':'cta','text':'COMENTE SÓ O NÚMERO.','small':'Compartilhe para transformar julgamento em acolhimento.','dur':8.4,'start':12,'progress':650}
]

DYS=[
 {'src':'d_phone','mode':'hook','text':'OS NÚMEROS NÃO PARAM QUIETOS QUANDO VOCÊ PRECISA DELES.','dur':1.5,'start':0,'progress':20,'time':'07:54','size':48},
 {'src':'d_ticket','mode':'hook','text':'ACOMPANHE 1 MANHÃ.','dur':1.3,'start':0,'progress':35,'time':'08:14'},
 {'src':'d_pay','mode':'hook','text':'SEM VOLTAR O VÍDEO.','dur':1.4,'start':0,'progress':50,'time':'08:31'},
 {'src':'d_phone','mode':'task','label':'MISSÃO 1 • HORA','wrong':'07:54','right':'07:45','text':'Você já conferiu três vezes.','dur':4.8,'start':2,'progress':100,'time':'07:45'},
 {'src':'d_ticket','mode':'task','label':'MISSÃO 2 • ROTA','wrong':'174','right':'147','text':'Um dígito troca todo o caminho.','dur':4.8,'start':2,'progress':160,'time':'08:12'},
 {'src':'d_pay','mode':'task','label':'MISSÃO 3 • PAGAR','wrong':'86,90','right':'68,90','text':'A fila cresce. A conta embaralha.','dur':4.8,'start':2,'progress':220,'time':'12:08'},
 {'src':'d_atm','mode':'task','label':'MISSÃO 4 • SENHA','wrong':'6381','right':'6831','text':'Você sabia. Até a tela pedir.','dur':4.8,'start':1,'progress':280,'time':'12:11'},
 {'src':'d_cash','mode':'task','label':'MISSÃO 5 • TROCO','wrong':'17,50','right':'15,70','text':'O valor parece certo… ou não.','dur':4.8,'start':1,'progress':340,'time':'12:13'},
 {'src':'d_card','mode':'turn','text':'ISSO NÃO É UMA PROVA DE INTELIGÊNCIA.','dur':4.0,'start':3,'progress':390,'time':'12:14','size':47},
 {'src':'d_ticket','mode':'truth','text':'PODE SER UMA DIFICULDADE PERSISTENTE COM QUANTIDADES, SEQUÊNCIAS E CÁLCULOS.','dur':4.8,'start':7,'progress':440,'time':'16:20','size':39},
 {'src':'d_phone','mode':'truth','label':'O NOME POSSÍVEL','text':'DISCALCULIA','dur':3.8,'start':7,'progress':485,'time':'19:04','size':70},
 {'src':'d_pay','mode':'truth','label':'O QUE AJUDA','text':'TEMPO EXTRA. APOIO VISUAL. CALCULADORA.','dur':4.5,'start':6,'progress':530,'time':'19:06','size':43},
 {'src':'d_atm','mode':'truth','label':'IMPORTANTE','text':'ESTE VÍDEO NÃO É UM TESTE DIAGNÓSTICO.','dur':3.8,'start':5,'progress':570,'time':'19:08','size':43},
 {'src':'d_ticket','mode':'truth','label':'LEMBRETE','text':'DEUS NÃO MEDE NINGUÉM PELA RAPIDEZ DE UMA CONTA.','dur':4.4,'start':10,'progress':610,'time':'19:10','size':42},
 {'src':'d_phone','mode':'cta','text':'HORA • ROTA • PAGAMENTO • TROCO','small':'Comente a etapa mais difícil e envie para quem precisa de acolhimento.','dur':6.3,'start':12,'progress':650,'time':'19:12'}
]

def render_scene(src,ov,out,dur,start,style,i):
 if style=='miso':
  grade='eq=contrast=1.28:saturation=.70:brightness=-.025,unsharp=5:5:.65'
  zoom=f"scale=800:1422,crop=720:1280:x='40+22*sin(t*1.05+{i})':y='70+18*cos(t*.9)'"
 else:
  grade='eq=contrast=1.16:saturation=.82:brightness=-.005,colorbalance=bs=.025:gs=.01,unsharp=5:5:.45'
  zoom=f"scale=780:1387,crop=720:1280:x='30+15*sin(t*.65+{i})':y='53+11*cos(t*.55)'"
 filt=f"[0:v]{zoom},fps={FPS},{grade},format=yuv420p[bg];[1:v]format=rgba,fade=t=in:st=0:d=.06:alpha=1,fade=t=out:st={max(.1,dur-.08)}:d=.08:alpha=1[ov];[bg][ov]overlay=0:0:format=auto[v]"
 run(['ffmpeg','-y','-loglevel','error','-stream_loop','-1','-ss',str(start),'-i',str(src),'-loop','1','-i',str(ov),'-t',str(dur),'-filter_complex',filt,'-map','[v]','-an','-c:v','libx264','-preset','fast','-crf','18','-pix_fmt','yuv420p',str(out)])

def build(name,style,beats,preview):
 parts=[]; frames=[]
 for i,b in enumerate(beats):
  src=download(b['src']); ov=O/f'{name}_{i:02}.png'; part=P/f'{name}_{i:02}.mp4'
  (miso_overlay if style=='miso' else dys_overlay)(ov,b)
  render_scene(src,ov,part,b['dur'],b.get('start',0),style,i); parts.append(part)
  shot=PRE/f'{name}_{i:02}.jpg'; run(['ffmpeg','-y','-loglevel','error','-ss',str(b['dur']/2),'-i',str(part),'-frames:v','1',str(shot)]); frames.append(shot)
 sheet=Image.new('RGB',(900,((len(frames)+4)//5)*320),(14,14,18))
 for i,f in enumerate(frames):
  im=Image.open(f).convert('RGB'); im.thumbnail((180,320)); sheet.paste(im,((i%5)*180,(i//5)*320))
 sheet.save(PRE/f'{name}_contato.jpg',quality=90)
 if preview:return
 lst=P/f'{name}.txt'; lst.write_text(''.join(f"file '{p.resolve()}'\n" for p in parts))
 base=P/f'{name}_base.mp4'; out=V/f'{name}.mp4'
 run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(lst),'-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p',str(base)])
 run(['ffmpeg','-y','-loglevel','error','-i',str(base),'-vf','scale=1080:1920:flags=lanczos','-an','-c:v','libx264','-preset','medium','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(out)])
 run(['ffprobe','-v','error','-show_entries','stream=width,height:format=duration,size','-of','default=noprint_wrappers=1',str(out)])

if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--preview',action='store_true'); x=ap.parse_args()
 build('Video_1_Desafio_sensorial_misofonia_v8','miso',MISO,x.preview)
 build('Video_2_POV_numeros_discalculia_v8','dys',DYS,x.preview)
