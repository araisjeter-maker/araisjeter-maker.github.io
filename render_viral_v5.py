import argparse, subprocess, time, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS=720,1280,30
ROOT=Path(__file__).parent
A=ROOT/"assets_v5"; O=ROOT/"overlays_v5"; P=ROOT/"parts_v5"; PRE=ROOT/"previews_v5"; V=ROOT/"videos"
for d in (A,O,P,PRE,V): d.mkdir(exist_ok=True)
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE=(255,255,255,255); INK=(29,22,32,255); LILAC=(154,104,178,255)
PALE=(235,213,242,255); DARK=(46,25,55,255); ROSE=(226,115,137,255)

SOURCES={
 "t1":"https://www.pexels.com/video/16666918/",
 "t2":"https://www.pexels.com/video/29376327/",
 "t3":"https://www.pexels.com/video/9010436/",
 "t4":"https://www.pexels.com/video/5137848/",
 "t5":"https://www.pexels.com/video/9465404/",
 "t6":"https://www.pexels.com/video/9465403/",
 "t7":"https://www.pexels.com/video/10210122/",
 "t8":"https://www.pexels.com/video/8921925/",
 "t9":"https://www.pexels.com/video/30428226/",
 "d1":"https://www.pexels.com/video/top-view-of-a-person-writing-in-a-journal-10673381/",
 "d2":"https://www.pexels.com/video/top-view-video-of-mobile-phone-and-study-materials-5087877/",
 "d3":"https://www.pexels.com/video/overhead-shot-of-a-person-writing-in-a-notebook-9683617/",
 "d4":"https://www.pexels.com/video/a-musician-and-songwriter-in-top-view-4705782/",
 "d5":"https://www.pexels.com/video/a-person-writing-a-love-letter-and-putting-it-in-an-envelop-6851677/",
 "d6":"https://www.pexels.com/video/close-up-shot-of-writing-materials-7744332/",
 "d7":"https://www.pexels.com/video/flipping-pages-of-a-notebook-6148847/",
 "d8":"https://www.pexels.com/video/top-view-of-a-man-reading-holy-bible-on-his-study-table-5206027/",
 "d9":"https://www.pexels.com/video/top-view-of-a-person-studying-6928974/",
 "d10":"https://www.pexels.com/video/a-person-filling-up-a-form-8060732/",
 "d11":"https://www.pexels.com/video/7034348/",
 "d12":"https://www.pexels.com/video/3580077/"
}
TKEYS=[f"t{i}" for i in range(1,10)]
DKEYS=[f"d{i}" for i in range(1,13)]
CANDIDATES={}
for keys in (TKEYS,DKEYS):
 for idx,key in enumerate(keys):
  order=keys[idx:]+keys[:idx]
  CANDIDATES[key]=[SOURCES[x] for x in order]

def run(cmd):
 print(" ".join(map(str,cmd)),flush=True); subprocess.run(cmd,check=True)

def download(key):
 out=A/f"{key}.mp4"
 if out.exists() and out.stat().st_size>100000:return out
 pages=CANDIDATES.get(key,[SOURCES[key]])
 for page in pages:
  video_id=re.search(r"(\d+)/?$",page).group(1)
  direct=[
   f"https://videos.pexels.com/video-files/{video_id}/{video_id}-hd_1920_1080_25fps.mp4",
   f"https://videos.pexels.com/video-files/{video_id}/{video_id}-hd_1080_1920_25fps.mp4",
   f"https://videos.pexels.com/video-files/{video_id}/{video_id}-hd_1920_1080_30fps.mp4",
   f"https://videos.pexels.com/video-files/{video_id}/{video_id}-hd_1080_1920_30fps.mp4",
   f"https://videos.pexels.com/video-files/{video_id}/{video_id}-hd_1280_720_25fps.mp4",
   f"https://videos.pexels.com/video-files/{video_id}/{video_id}-hd_720_1280_25fps.mp4"
  ]
  for url in direct:
   try:
    if out.exists():out.unlink()
    run(["curl","-L","--fail","--silent","--show-error","--connect-timeout","5","--max-time","120","-o",str(out),url])
    if out.exists() and out.stat().st_size>100000:return out
   except subprocess.CalledProcessError:
    pass
  try:
   if out.exists():out.unlink()
   run(["yt-dlp","--no-playlist","--impersonate","chrome","--extractor-args","generic:impersonate",
        "--referer",page,"--retries","3","-f","bestvideo[height<=1920][ext=mp4]/best[height<=1920]/best",
        "--merge-output-format","mp4","-o",str(out),page])
   if out.exists() and out.stat().st_size>100000:
    time.sleep(1);return out
  except subprocess.CalledProcessError:
   time.sleep(1)
 raise RuntimeError("Fontes gratuitas indisponíveis: "+key)

def ft(n,b=True):return ImageFont.truetype(BOLD if b else REG,n)
def tw(d,s,f):return d.textbbox((0,0),s,font=f)[2]
def wrap(d,s,f,m):
 lines=[];cur=""
 for word in s.split():
  test=(cur+" "+word).strip()
  if cur and tw(d,test,f)>m:lines.append(cur);cur=word
  else:cur=test
 if cur:lines.append(cur)
 return lines

def lines(d,text,x,y,f,fill,maxw,spacing=8,center=False):
 arr=wrap(d,text,f,maxw)
 for s in arr:
  xx=(W-tw(d,s,f))//2 if center else x
  d.text((xx,y),s,font=f,fill=fill,stroke_width=2,stroke_fill=(20,12,23,150))
  y+=f.size+spacing
 return y

def rotated_text(im,text,xy,size,color,angle):
 layer=Image.new("RGBA",(500,160),(0,0,0,0));d=ImageDraw.Draw(layer);d.text((15,15),text,font=ft(size),fill=color)
 layer=layer.rotate(angle,expand=True,resample=Image.Resampling.BICUBIC)
 im.alpha_composite(layer,xy)

def gradient(im,top=True):
 g=Image.new("RGBA",(W,420),(0,0,0,0)); gd=ImageDraw.Draw(g)
 for y in range(420):
  a=int(190*(1-y/420)) if top else int(190*y/420)
  gd.line((0,y,W,y),fill=(18,10,21,a))
 im.alpha_composite(g,(0,0 if top else H-420))

def overlay_pov(path,b,i,total):
 im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
 gradient(im,True);gradient(im,False)
 mode=b.get("mode","story"); text=b["text"]
 d.rounded_rectangle((28,28,272,68),18,fill=(46,25,55,222))
 d.text((43,40),"POV — ninguém viu",font=ft(17,False),fill=WHITE)
 d.text((645,38),f"{i+1:02}",font=ft(17),fill=PALE)
 if mode=="hook":
  d.rectangle((0,0,W,H),fill=(24,13,29,145))
  lines(d,text,38,430,ft(b.get("size",72)),WHITE,644,7,True)
  d.rounded_rectangle((80,705,640,715),5,fill=ROSE)
 elif mode=="impact":
  d.rectangle((0,0,W,H),fill=(24,13,29,174))
  lines(d,text,36,470,ft(b.get("size",86)),WHITE,648,6,True)
 elif mode=="timer":
  d.rounded_rectangle((42,160,678,470),35,fill=(30,17,36,210))
  d.text((70,185),b.get("clock","01:00"),font=ft(112),fill=WHITE)
  d.text((73,330),"tentando parecer imóvel",font=ft(24,False),fill=PALE)
  lines(d,text,43,760,ft(50),WHITE,630,6)
 elif mode=="split":
  d.rounded_rectangle((32,150,688,420),34,fill=(25,15,30,218))
  d.text((58,176),"POR FORA",font=ft(19,False),fill=PALE)
  lines(d,text,58,224,ft(48),WHITE,580,5)
  d.rounded_rectangle((32,780,688,1070),34,fill=(125,77,146,232))
  d.text((58,806),"POR DENTRO",font=ft(19,False),fill=WHITE)
  lines(d,b.get("small",""),58,858,ft(46),WHITE,580,5)
 elif mode=="final":
  d.rectangle((0,0,W,H),fill=(36,19,43,210))
  lines(d,text,48,270,ft(63),WHITE,624,7,True)
  d.rounded_rectangle((44,820,676,1005),38,fill=(247,235,249,248))
  lines(d,b.get("small",""),74,855,ft(27),DARK,570,6,True)
 else:
  y=b.get("y",190 if i%2==0 else 760)
  lines(d,text,38,y,ft(b.get("size",54)),WHITE,640,6)
  if b.get("small"):lines(d,b["small"],40,y+205,ft(25,False),PALE,620,4)
 d.text((28,1218),"@fealemdodiagnostico",font=ft(15,False),fill=WHITE)
 d.rounded_rectangle((390,1228,690,1237),5,fill=(255,255,255,60))
 d.rounded_rectangle((390,1228,390+int(300*(i+1)/total),1237),5,fill=ROSE)
 im.save(path)

def overlay_language(path,b,i,total):
 im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
 gradient(im,True);gradient(im,False)
 mode=b.get("mode","note"); text=b["text"]
 d.rounded_rectangle((28,28,330,68),18,fill=(246,235,221,235))
 d.text((43,40),"10 segundos por dentro",font=ft(17,False),fill=DARK)
 d.text((650,38),f"{i+1:02}",font=ft(17),fill=WHITE)
 if mode=="hook":
  d.rectangle((0,0,W,H),fill=(238,218,242,170))
  d.rounded_rectangle((38,310,682,835),42,fill=(251,244,231,246))
  lines(d,text,68,405,ft(b.get("size",68)),DARK,585,8,True)
 elif mode=="cursor":
  d.rounded_rectangle((38,245,682,905),40,fill=(251,245,232,246))
  d.text((68,285),"A resposta estava aqui:",font=ft(24,False),fill=DARK)
  lines(d,text,68,430,ft(59),DARK,575,7)
  d.rectangle((68,625,87,715),fill=LILAC)
  d.text((68,785),"mas a palavra não chegava.",font=ft(23),fill=ROSE)
 elif mode=="timer":
  d.rectangle((0,0,W,H),fill=(43,25,50,158))
  d.text((52,245),b.get("clock","05"),font=ft(188),fill=WHITE)
  d.text((430,390),"segundos",font=ft(28,False),fill=PALE)
  lines(d,text,48,770,ft(48),WHITE,620,6)
 elif mode=="scatter":
  d.rounded_rectangle((34,175,686,1070),40,fill=(248,239,225,244))
  pts=[(64,250),(350,390),(95,610),(330,805)]
  for word,(x,y) in zip(text.split("|"),pts):
   d.rounded_rectangle((x,y,x+270,y+92),25,fill=(221,194,230,255))
   d.text((x+22,y+25),word,font=ft(34),fill=DARK)
 elif mode=="assemble":
  d.rounded_rectangle((34,160,686,1080),40,fill=(248,239,225,244))
  d.text((62,205),"Quando as palavras travarem:",font=ft(25),fill=DARK)
  yy=330
  for n,part in enumerate(text.split("|"),1):
   d.ellipse((62,yy,124,yy+62),fill=LILAC)
   d.text((84,yy+14),str(n),font=ft(24),fill=WHITE)
   lines(d,part,150,yy+8,ft(34),DARK,470,4); yy+=205
 elif mode=="final":
  d.rectangle((0,0,W,H),fill=(235,216,241,218))
  d.rounded_rectangle((38,220,682,720),44,fill=(251,244,231,248))
  lines(d,text,70,305,ft(54),DARK,580,8,True)
  lines(d,b.get("small",""),64,855,ft(27),WHITE,590,6,True)
 else:
  y=b.get("y",210 if i%2==0 else 725)
  d.rounded_rectangle((30,y-35,690,y+245),34,fill=(36,22,42,205))
  lines(d,text,54,y,ft(b.get("size",52)),WHITE,610,6)
  if b.get("small"):lines(d,b["small"],54,y+170,ft(24,False),PALE,600,4)
 d.text((28,1218),"@fealemdodiagnostico",font=ft(15,False),fill=WHITE)
 d.rounded_rectangle((390,1228,690,1237),5,fill=(255,255,255,60))
 d.rounded_rectangle((390,1228,390+int(300*(i+1)/total),1237),5,fill=LILAC)
 im.save(path)

def render_part(src,ov,out,dur,start,style,direction):
 sat=.72 if style=="pov" else .88
 color=f"eq=contrast=1.16:saturation={sat}:brightness=-0.035,unsharp=5:5:0.4"
 slide="if(lt(t,0.20),28*(1-t/0.20),0)" if direction>0 else "if(lt(t,0.20),-28*(1-t/0.20),0)"
 filt=(f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}:"
       f"x='(iw-ow)*(0.5+0.04*sin(t*1.1))':y='(ih-oh)/2',fps={FPS},{color},format=yuv420p[bg];"
       f"[1:v]format=rgba,fade=t=in:st=0:d=0.14:alpha=1,fade=t=out:st={dur-0.12:.2f}:d=0.12:alpha=1[tx];"
       f"[bg][tx]overlay=x='{slide}':y=0:format=auto[v]")
 run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",str(start),"-i",str(src),
      "-loop","1","-i",str(ov),"-t",str(dur),"-filter_complex",filt,"-map","[v]","-an",
      "-c:v","libx264","-preset","fast","-crf","18","-pix_fmt","yuv420p",str(out)])

def contact_sheet(name,frames):
 thumbs=[]
 for p in frames:
  im=Image.open(p).convert("RGB");im.thumbnail((270,480));thumbs.append(im.copy())
 cols=4;rows=(len(thumbs)+cols-1)//cols
 sheet=Image.new("RGB",(cols*270,rows*480),(24,16,28))
 for i,im in enumerate(thumbs):sheet.paste(im,((i%cols)*270,(i//cols)*480))
 sheet.save(PRE/f"{name}_contato.jpg",quality=88)

def build(name,style,beats,preview_only):
 parts=[];frames=[]
 for i,b in enumerate(beats):
  src=download(b["src"]);ov=O/f"{name}_{i:02}.png";part=P/f"{name}_{i:02}.mp4";jpg=PRE/f"{name}_{i:02}.jpg"
  (overlay_pov if style=="pov" else overlay_language)(ov,b,i,len(beats))
  render_part(src,ov,part,b["dur"],b.get("start",0),style,1 if i%2==0 else -1)
  run(["ffmpeg","-y","-loglevel","error","-ss",str(b["dur"]/2),"-i",str(part),"-frames:v","1",str(jpg)])
  parts.append(part);frames.append(jpg)
 contact_sheet(name,frames)
 if preview_only:return
 listing=P/f"{name}.txt";listing.write_text("".join(f"file '{x.resolve()}'\n" for x in parts))
 base=P/f"{name}_base.mp4";out=V/f"{name}.mp4"
 run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(listing),"-an",
      "-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",str(base)])
 run(["ffmpeg","-y","-loglevel","error","-i",str(base),"-vf","scale=1080:1920:flags=lanczos","-an",
      "-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",str(out)])
 run(["ffprobe","-v","error","-show_entries","stream=width,height:format=duration,size","-of","default=noprint_wrappers=1",str(out)])

TOURETTE=[
 {"src":"t1","text":"EU SEGUREI","mode":"hook","dur":0.85,"start":0,"size":78},
 {"src":"t5","text":"MEU TIQUE","mode":"hook","dur":0.85,"start":1,"size":76},
 {"src":"t2","text":"POR 8 MINUTOS.","mode":"hook","dur":1.25,"start":0,"size":67},
 {"src":"t1","text":"Eu estava na fila do mercado.","dur":2.5,"start":2},
 {"src":"t5","text":"O primeiro movimento veio.","dur":2.3,"start":3},
 {"src":"t2","text":"Olhei para os lados.","dur":2.2,"start":2},
 {"src":"t6","text":"E fiz o que aprendi a fazer:","dur":2.5,"start":4,"size":49},
 {"src":"t2","text":"SEGUREI.","mode":"impact","dur":2.0,"start":1},
 {"src":"t3","text":"Um minuto.","mode":"timer","clock":"01:00","dur":2.3,"start":0},
 {"src":"t5","text":"Mandíbula.","mode":"impact","dur":2.0,"start":6},
 {"src":"t6","text":"Pescoço.","mode":"impact","dur":2.0,"start":7},
 {"src":"t6","text":"Mãos.","mode":"impact","dur":2.0,"start":5},
 {"src":"t4","text":"Eu ainda estava segurando.","mode":"timer","clock":"04:00","dur":2.5,"start":1},
 {"src":"t1","text":"Eu parecia parado.","mode":"split","small":"Tudo apertava ao mesmo tempo.","dur":3.2,"start":6},
 {"src":"t3","text":"Ninguém percebeu a força que aquilo exigia.","dur":3.2,"start":1,"size":45},
 {"src":"t2","text":"Até que finalmente saí.","mode":"timer","clock":"08:00","dur":2.8,"start":6},
 {"src":"t2","text":"Longe dos olhares...","dur":2.4,"start":1},
 {"src":"t5","text":"meu corpo soltou tudo de uma vez.","dur":3.2,"start":9,"size":48},
 {"src":"t5","text":"Não era falta de educação.","dur":3.0,"start":4},
 {"src":"t6","text":"Era sobrevivência.","mode":"impact","dur":2.7,"start":10},
 {"src":"t3","text":"Julgar dura segundos.","dur":2.7,"start":5},
 {"src":"t4","text":"O peso pode durar o dia inteiro.","dur":3.0,"start":6},
 {"src":"t6","text":"Você já se escondeu para caber?","mode":"final","small":"Comente “EU ENTENDO” e compartilhe com quem precisa parar de julgar.","dur":4.8,"start":7}
]

TDL=[
 {"src":"d1","text":"EU SABIA","mode":"hook","dur":0.9,"start":0,"size":78},
 {"src":"d11","text":"A RESPOSTA.","mode":"hook","dur":0.9,"start":0,"size":70},
 {"src":"d2","text":"MAS ELA NÃO SAÍA.","mode":"hook","dur":1.2,"start":1,"size":58},
 {"src":"d3","text":"A pergunta chegou.","dur":2.4,"start":2},
 {"src":"d4","text":"Minha cabeça respondeu primeiro.","dur":2.7,"start":1,"size":47},
 {"src":"d3","text":"Só faltava uma coisa:","dur":2.2,"start":2},
 {"src":"d1","text":"a primeira palavra.","mode":"cursor","dur":2.7,"start":5},
 {"src":"d11","text":"Todo mundo esperando.","mode":"timer","clock":"05","dur":2.4,"start":1},
 {"src":"d10","text":"O silêncio virou pressão.","dur":2.6,"start":1},
 {"src":"d12","text":"A palavra ainda não vinha.","mode":"timer","clock":"10","dur":2.4,"start":2},
 {"src":"d8","text":"“Você não estudou?”","dur":2.6,"start":2},
 {"src":"d8","text":"Eu estudei.","dur":2.2,"start":1},
 {"src":"d9","text":"Eu sabia.","dur":2.2,"start":3},
 {"src":"d10","text":"Mas a pressão embaralhou tudo.","dur":2.7,"start":2},
 {"src":"d2","text":"palavra|ordem|tempo|voz","mode":"scatter","dur":3.2,"start":5},
 {"src":"d3","text":"Não é falta de inteligência.","dur":3.0,"start":6},
 {"src":"d4","text":"É acesso à linguagem.","dur":2.8,"start":6},
 {"src":"d9","text":"Uma pergunta|Uma pausa de verdade|Um apoio visual","mode":"assemble","dur":4.1,"start":7},
 {"src":"d4","text":"Às vezes, apoiar é parar de apressar.","dur":3.5,"start":6,"size":47},
 {"src":"d3","text":"Quanto tempo você daria?","dur":3.0,"start":8},
 {"src":"d9","text":"Tempo não é incapacidade.","dur":3.1,"start":8},
 {"src":"d8","text":"10 segundos podem mudar uma resposta.","mode":"final","small":"Envie para quem ainda confunde uma pausa com incapacidade.","dur":4.8,"start":9}
]

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--preview",action="store_true");args=ap.parse_args()
 build("Video_1_Tourette_POV_viral_v5","pov",TOURETTE,args.preview)
 build("Video_2_TDL_10segundos_viral_v5","language",TDL,args.preview)
