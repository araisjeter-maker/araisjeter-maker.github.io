import argparse, subprocess, re, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=720,1280,30
ROOT=Path(__file__).parent
A=ROOT/"assets_v6"; O=ROOT/"overlays_v6"; P=ROOT/"parts_v6"; V=ROOT/"videos"; PRE=ROOT/"previews_v6"
for d in (A,O,P,V,PRE): d.mkdir(exist_ok=True)
B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
R="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
S="/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
INK=(31,25,35,255); WHITE=(255,255,255,255); LILAC=(170,118,191,255)
PALE=(242,225,247,255); CREAM=(250,244,231,255); CORAL=(235,112,124,255); GOLD=(245,199,84,255)

SRC={
 "q1":"https://www.pexels.com/video/time-lapse-video-of-a-person-pushing-a-grocery-cart-4309719/",
 "q2":"https://www.pexels.com/video/food-market-supermarket-foodstuff-4251604/",
 "q3":"https://www.pexels.com/video/time-lapse-video-of-a-person-pushing-the-grocery-cart-4309734/",
 "q4":"https://www.pexels.com/video/a-person-putting-groceries-on-a-shopping-cart-9010435/",
 "q5":"https://www.pexels.com/video/a-couple-pushing-the-shopping-cart-in-the-grocery-4121748/",
 "n1":"https://www.pexels.com/video/man-making-a-sticky-note-at-work-desk-6177768/",
 "n2":"https://www.pexels.com/video/person-writing-on-a-paper-8872970/",
 "n3":"https://www.pexels.com/video/hand-flipping-through-empty-notebook-pages-6177794/",
 "n4":"https://www.pexels.com/video/a-person-writing-in-the-notebook-9305503/",
 "n5":"https://www.pexels.com/video/person-writing-on-a-notebook-6386551/",
 "n6":"https://www.pexels.com/video/close-up-video-of-a-person-writing-7969377/"
}

def run(c):
 print(" ".join(map(str,c)),flush=True); subprocess.run(c,check=True)

def download(k):
 out=A/f"{k}.mp4"
 if out.exists() and out.stat().st_size>100000:return out
 page=SRC[k]; vid=re.search(r"(\d+)/?$",page).group(1)
 urls=[
  f"https://videos.pexels.com/video-files/{vid}/{vid}-hd_1080_1920_25fps.mp4",
  f"https://videos.pexels.com/video-files/{vid}/{vid}-hd_1920_1080_25fps.mp4",
  f"https://videos.pexels.com/video-files/{vid}/{vid}-hd_1080_1920_30fps.mp4",
  f"https://videos.pexels.com/video-files/{vid}/{vid}-hd_1920_1080_30fps.mp4",
  f"https://videos.pexels.com/video-files/{vid}/{vid}-hd_720_1280_25fps.mp4",
  f"https://videos.pexels.com/video-files/{vid}/{vid}-hd_1280_720_25fps.mp4"]
 for url in urls:
  try:
   run(["curl","-L","--fail","--silent","--show-error","--connect-timeout","6","--max-time","150","-o",str(out),url])
   if out.stat().st_size>100000:return out
  except Exception:
   if out.exists():out.unlink()
 run(["yt-dlp","--no-playlist","--impersonate","chrome","--referer",page,"-f","bestvideo[height<=1920][ext=mp4]/best[height<=1920]","--merge-output-format","mp4","-o",str(out),page])
 return out

def font(n,b=True,serif=False): return ImageFont.truetype(S if serif else (B if b else R),n)
def width(d,t,f): return d.textbbox((0,0),t,font=f)[2]
def wrap(d,t,f,maxw):
 out=[]; cur=""
 for w in t.split():
  test=(cur+" "+w).strip()
  if cur and width(d,test,f)>maxw: out.append(cur);cur=w
  else: cur=test
 if cur:out.append(cur)
 return out
def draw_lines(d,t,y,f,fill,maxw=620,center=True,shadow=True,spacing=7,x=50):
 arr=wrap(d,t,f,maxw)
 for line in arr:
  xx=(W-width(d,line,f))//2 if center else x
  if shadow:d.text((xx+3,y+4),line,font=f,fill=(0,0,0,150))
  d.text((xx,y),line,font=f,fill=fill)
  y+=f.size+spacing
 return y

def tourette_overlay(path,b):
 im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
 mode=b["mode"]; text=b["text"]
 if mode=="hook":
  d.rectangle((0,0,W,8),fill=CORAL)
  draw_lines(d,text,96,font(b.get("size",68)),WHITE,640)
  d.rounded_rectangle((232,270,488,313),21,fill=(31,25,35,205))
  d.text((260,281),"UMA CENA REAL",font=font(17,False),fill=PALE)
 elif mode=="flash":
  d.rectangle((0,0,W,H),fill=(24,16,27,55))
  f=font(b.get("size",88))
  draw_lines(d,text,520,f,WHITE,650)
 elif mode=="thought":
  d.rounded_rectangle((44,835,676,1035),28,fill=(26,20,30,210),outline=(201,153,218,220),width=2)
  d.text((70,858),"PENSAMENTO INTERNO",font=font(15,False),fill=(211,170,225,255))
  draw_lines(d,text,904,font(b.get("size",38)),WHITE,555,center=False,x=72)
 elif mode=="pressure":
  for j,word in enumerate(["SEGURA","DISFARÇA","SORRI"]):
   y=230+j*180
   alpha=235 if word==text else 75
   f=font(72)
   x=(W-width(d,word,f))//2
   d.text((x+3,y+4),word,font=f,fill=(0,0,0,120))
   d.text((x,y),word,font=f,fill=(255,255,255,alpha))
  d.rectangle((140,782,580,790),fill=CORAL)
 elif mode=="release":
  d.rectangle((0,0,W,H),fill=(95,51,111,105))
  draw_lines(d,text,430,font(62),WHITE,640)
  d.ellipse((316,690,404,778),outline=PALE,width=5)
  d.line((360,710,360,755),fill=PALE,width=5)
 elif mode=="truth":
  d.rounded_rectangle((38,110,682,375),32,fill=(248,240,250,240))
  draw_lines(d,text,155,font(48),INK,570,shadow=False)
 elif mode=="final":
  d.rectangle((0,0,W,H),fill=(35,23,39,190))
  d.text((50,160),"ANTES DE JULGAR,",font=font(28,False),fill=PALE)
  draw_lines(d,text,255,font(58),WHITE,625,center=False,x=50)
  d.rounded_rectangle((50,900,670,1045),30,fill=(246,231,249,245))
  draw_lines(d,b["small"],930,font(25),INK,550,shadow=False)
 d.text((32,1218),"@fealemdodiagnostico",font=font(15,False),fill=WHITE)
 im.save(path)

def tdl_overlay(path,b):
 im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
 mode=b["mode"]; text=b["text"]
 if mode=="hook":
  d.polygon([(30,110),(690,72),(676,420),(42,452)],fill=(250,244,231,242))
  d.line((42,420,676,388),fill=LILAC,width=8)
  draw_lines(d,text,155,font(b.get("size",54),serif=True),INK,575,shadow=False)
 elif mode=="test":
  d.rounded_rectangle((48,150,672,870),22,fill=(253,248,237,238))
  d.text((76,186),"TESTE RÁPIDO",font=font(18,False),fill=LILAC)
  d.text((548,180),b["clock"],font=font(58),fill=CORAL)
  d.line((76,272,644,272),fill=(214,192,218,255),width=2)
  draw_lines(d,text,350,font(44,serif=True),INK,545,shadow=False)
  d.rounded_rectangle((92,625,628,718),18,fill=(236,216,242,255))
  d.text((120,647),b.get("blank","________________"),font=font(31,False),fill=INK)
  d.text((78,792),"Não role ainda.",font=font(18,False),fill=(95,78,99,255))
 elif mode=="reveal":
  d.rounded_rectangle((42,170,678,930),28,fill=(253,248,237,240))
  d.text((72,210),"A PALAVRA ERA:",font=font(18,False),fill=LILAC)
  draw_lines(d,text,365,font(74,serif=True),INK,575,shadow=False)
  d.rectangle((95,540,625,554),fill=GOLD)
  draw_lines(d,b["small"],650,font(30),INK,540,shadow=False)
 elif mode=="note":
  d.polygon([(55,180),(660,155),(676,910),(42,945)],fill=(250,244,231,238))
  d.line((75,320,638,295),fill=(216,198,211,255),width=2)
  d.text((82,220),b.get("tag","O QUE ACONTECE"),font=font(17,False),fill=LILAC)
  draw_lines(d,text,380,font(b.get("size",39),serif=True),INK,535,shadow=False)
  if b.get("small"):
   d.rounded_rectangle((78,720,640,838),18,fill=(234,216,239,255))
   draw_lines(d,b["small"],748,font(24),INK,500,shadow=False)
 elif mode=="steps":
  d.rounded_rectangle((42,120,678,1010),30,fill=(250,244,231,241))
  d.text((76,165),"FAÇA ASSIM",font=font(19,False),fill=LILAC)
  yy=295
  for n,line in enumerate(text.split("|"),1):
   d.ellipse((75,yy,135,yy+60),fill=LILAC)
   d.text((96,yy+14),str(n),font=font(23),fill=WHITE)
   draw_lines(d,line,yy+8,font(31,serif=True),INK,470,center=False,shadow=False,x=160)
   yy+=205
 elif mode=="final":
  d.rectangle((0,0,W,H),fill=(239,220,244,185))
  d.polygon([(32,170),(685,120),(670,825),(48,880)],fill=(252,246,234,247))
  draw_lines(d,text,260,font(51,serif=True),INK,570,shadow=False)
  d.line((100,665,620,665),fill=CORAL,width=8)
  draw_lines(d,b["small"],940,font(25),WHITE,590)
 d.text((32,1218),"@fealemdodiagnostico",font=font(15,False),fill=WHITE)
 im.save(path)

def render_scene(src,ov,out,dur,start,style,i):
 if style=="tourette":
  grade="eq=contrast=1.13:saturation=.88:brightness=.015,unsharp=5:5:.45"
  zoom=f"scale=760:1350,crop=720:1280:x='20+10*sin(t*1.2+{i})':y='35+8*cos(t*.9)'"
 else:
  grade="eq=contrast=1.06:saturation=.82:brightness=.045,colorbalance=rs=.02:gs=.01:bs=.03"
  zoom=f"scale=750:1334,crop=720:1280:x='15+8*sin(t*.7+{i})':y='27+6*cos(t*.8)'"
 filt=f"[0:v]{zoom},fps={FPS},{grade},format=yuv420p[bg];[1:v]format=rgba,fade=t=in:st=0:d=.10:alpha=1,fade=t=out:st={max(.1,dur-.12)}:d=.12:alpha=1[ov];[bg][ov]overlay=0:0:format=auto[v]"
 run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",str(start),"-i",str(src),"-loop","1","-i",str(ov),"-t",str(dur),"-filter_complex",filt,"-map","[v]","-an","-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",str(out)])

TOURETTE=[
 {"src":"q1","mode":"hook","text":"VOCÊ PERCEBERIA?","dur":1.2,"start":0},
 {"src":"q3","mode":"flash","text":"O TIQUE VEIO.","dur":1.1,"start":1,"size":72},
 {"src":"q5","mode":"flash","text":"EU ESCONDI.","dur":1.7,"start":0,"size":76},
 {"src":"q1","mode":"thought","text":"Só preciso chegar ao caixa.","dur":3.3,"start":2},
 {"src":"q3","mode":"thought","text":"Meu pescoço quer se mover.","dur":3.0,"start":4},
 {"src":"q5","mode":"thought","text":"Tem gente olhando?","dur":3.4,"start":2},
 {"src":"q2","mode":"pressure","text":"SEGURA","dur":3.0,"start":1},
 {"src":"q4","mode":"thought","text":"Respira. Continua andando.","dur":3.4,"start":3},
 {"src":"q3","mode":"pressure","text":"DISFARÇA","dur":3.0,"start":7},
 {"src":"q5","mode":"thought","text":"A mandíbula dói agora.","dur":3.3,"start":5},
 {"src":"q1","mode":"pressure","text":"SORRI","dur":3.0,"start":8},
 {"src":"q2","mode":"thought","text":"Por fora: uma compra comum.","dur":3.6,"start":7},
 {"src":"q4","mode":"thought","text":"Por dentro: meu corpo em alerta.","dur":3.2,"start":9},
 {"src":"q5","mode":"thought","text":"A porta finalmente apareceu.","dur":3.3,"start":8},
 {"src":"q1","mode":"release","text":"LÁ FORA, EU SOLTEI.","dur":3.4,"start":11},
 {"src":"q3","mode":"truth","text":"Não era falta de educação.","dur":3.5,"start":10},
 {"src":"q2","mode":"truth","text":"Era o preço de parecer “normal”.","dur":3.3,"start":12},
 {"src":"q4","mode":"thought","text":"Quantas pessoas vivem isso em silêncio?","dur":3.5,"start":13,"size":34},
 {"src":"q1","mode":"final","text":"UM TIQUE NÃO PRECISA DA SUA APROVAÇÃO.","small":"Compartilhe para trocar julgamento por acolhimento.","dur":4.8,"start":15}
]

TDL=[
 {"src":"n1","mode":"hook","text":"FAÇA ESTE TESTE SEM FALAR.","dur":1.2,"start":0},
 {"src":"n3","mode":"hook","text":"VOCÊ TEM 10 SEGUNDOS.","dur":1.2,"start":1},
 {"src":"n2","mode":"hook","text":"NÃO VALE PULAR.","dur":1.6,"start":0,"size":62},
 {"src":"n1","mode":"test","text":"Complete a frase: “Eu guardei a comida na...”","blank":"g   l   a   e   d   i   r   a","clock":"10","dur":2.0,"start":2},
 {"src":"n2","mode":"test","text":"A palavra parece próxima.","blank":"g   l   a   e   d   i   r   a","clock":"08","dur":2.0,"start":2},
 {"src":"n4","mode":"test","text":"Mas as letras não se organizam.","blank":"d   a   r   e   i   g   l   a","clock":"06","dur":2.0,"start":4},
 {"src":"n5","mode":"test","text":"Todo mundo está esperando.","blank":"g   e   l   a   d   e   i   r   a","clock":"04","dur":2.0,"start":2},
 {"src":"n6","mode":"test","text":"Agora responda.","blank":"________________","clock":"02","dur":2.0,"start":3},
 {"src":"n3","mode":"reveal","text":"GELADEIRA","small":"Você sabia. Só precisou de tempo.","dur":3.2,"start":4},
 {"src":"n1","mode":"note","tag":"AGORA IMAGINE","text":"Sentir essa pressão em perguntas simples, todos os dias.","dur":3.0,"start":6},
 {"src":"n2","mode":"note","text":"No TDL, saber e conseguir colocar em palavras não são a mesma coisa.","dur":3.2,"start":6,"size":35},
 {"src":"n4","mode":"note","text":"A resposta pode existir antes da palavra aparecer.","dur":3.0,"start":7},
 {"src":"n5","mode":"note","text":"Pressa não acelera a linguagem.","small":"Muitas vezes, ela bloqueia ainda mais.","dur":3.4,"start":5},
 {"src":"n6","mode":"note","text":"Silêncio não significa falta de inteligência.","dur":3.2,"start":7},
 {"src":"n3","mode":"note","text":"Uma pausa verdadeira muda a experiência.","dur":3.4,"start":8},
 {"src":"n1","mode":"steps","text":"Faça uma pergunta por vez.|Espere sem completar a frase.|Ofereça apoio visual.","dur":3.2,"start":10},
 {"src":"n2","mode":"note","text":"Acolher também é desacelerar.","dur":3.5,"start":10},
 {"src":"n4","mode":"note","text":"Dez segundos podem devolver autonomia.","dur":3.5,"start":11},
 {"src":"n5","mode":"note","text":"Você teria esperado?","small":"Responda nos comentários: SIM ou NÃO.","dur":3.4,"start":9},
 {"src":"n6","mode":"note","text":"Envie este teste a quem ainda confunde pausa com incapacidade.","dur":3.2,"start":12,"size":34},
 {"src":"n3","mode":"final","text":"TEMPO NÃO É INCAPACIDADE.","small":"Informação também é uma forma de cuidado.","dur":4.8,"start":12}
]

def build(name,style,beats,preview):
 parts=[]; frames=[]
 for i,b in enumerate(beats):
  src=download(b["src"]); ov=O/f"{name}_{i:02}.png"; part=P/f"{name}_{i:02}.mp4"
  (tourette_overlay if style=="tourette" else tdl_overlay)(ov,b)
  render_scene(src,ov,part,b["dur"],b.get("start",0),style,i); parts.append(part)
  shot=PRE/f"{name}_{i:02}.jpg"
  run(["ffmpeg","-y","-loglevel","error","-ss",str(b["dur"]/2),"-i",str(part),"-frames:v","1",str(shot)]);frames.append(shot)
 thumbs=[]
 for f in frames:
  im=Image.open(f).convert("RGB");im.thumbnail((180,320));thumbs.append(im.copy())
 sheet=Image.new("RGB",(900,((len(thumbs)+4)//5)*320),(20,15,22))
 for i,im in enumerate(thumbs):sheet.paste(im,((i%5)*180,(i//5)*320))
 sheet.save(PRE/f"{name}_contato.jpg",quality=88)
 if preview:return
 lst=P/f"{name}.txt";lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
 base=P/f"{name}_base.mp4"; out=V/f"{name}.mp4"
 run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),"-an","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",str(base)])
 run(["ffmpeg","-y","-loglevel","error","-i",str(base),"-vf","scale=1080:1920:flags=lanczos","-an","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",str(out)])
 run(["ffprobe","-v","error","-show_entries","stream=width,height:format=duration,size","-of","default=noprint_wrappers=1",str(out)])

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--preview",action="store_true");x=ap.parse_args()
 build("Video_1_Tourette_microhistoria_v6","tourette",TOURETTE,x.preview)
 build("Video_2_TDL_teste_visual_v6","tdl",TDL,x.preview)
