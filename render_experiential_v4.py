import argparse, subprocess, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS=720,1280,30
ROOT=Path(__file__).parent
A=ROOT/"assets_v4"; O=ROOT/"overlays_v4"; P=ROOT/"parts_v4"; PRE=ROOT/"previews_v4"; V=ROOT/"videos"
for d in (A,O,P,PRE,V): d.mkdir(exist_ok=True)
BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
WHITE=(255,255,255,255); INK=(29,22,32,255); LILAC=(154,104,178,255)
PALE=(235,213,242,255); DARK=(46,25,55,255); ROSE=(226,115,137,255)

SOURCES={
 "t1":"https://www.pexels.com/video/a-man-looking-anxious-6605949/",
 "t2":"https://www.pexels.com/video/tired-man-sitting-on-chair-7660187/",
 "t3":"https://www.pexels.com/video/man-with-fear-of-being-alone-8458497/",
 "t4":"https://www.pexels.com/video/woman-comforting-sad-twin-sister-6764083/",
 "t5":"https://www.pexels.com/video/same-sex-couple-lying-on-the-floor-holding-hands-6973129/",
 "t6":"https://www.pexels.com/video/a-woman-touching-a-man-s-face-8088655/",
 "t7":"https://www.pexels.com/video/a-shopping-cart-roaming-the-supermarket-5137848/",
 "t8":"https://www.pexels.com/video/a-close-up-of-a-person-s-hand-10210122/",
 "t9":"https://www.pexels.com/video/woman-resting-her-head-on-her-hand-6382082/",
 "t10":"https://www.pexels.com/video/close-up-video-of-hands-moving-9465403/",
 "d1":"https://www.pexels.com/video/close-up-view-of-a-man-looking-worried-7534959/",
 "d2":"https://www.pexels.com/video/close-up-view-of-a-person-typing-7660185/",
 "d3":"https://www.pexels.com/video/a-person-reading-a-book-4769627/",
 "d4":"https://www.pexels.com/video/woman-wearing-a-silver-watch-8995391/",
 "d5":"https://www.pexels.com/video/brain-27168144/",
 "d6":"https://www.pexels.com/video/man-listening-to-someone-talk-7581218/",
 "d7":"https://www.pexels.com/video/a-woman-talking-to-someone-10373944/",
 "d8":"https://www.pexels.com/video/close-up-shot-of-humans-hands-9465404/"
}
CANDIDATES={
 "t2":[
  "https://www.pexels.com/video/tired-man-sitting-on-chair-7660187/",
  "https://www.pexels.com/video/a-stressed-man-holding-his-head-7918580/",
  "https://www.pexels.com/video/a-couple-holding-hands-8921925/"
 ],
 "t4":[
  "https://www.pexels.com/video/woman-comforting-sad-twin-sister-6764083/",
  "https://www.pexels.com/video/a-woman-nodding-while-talking-9034495/",
  "https://www.pexels.com/video/a-couple-holding-hands-8921925/"
 ],
 "t1":[
  "https://www.pexels.com/video/a-man-looking-anxious-6605949/",
  "https://www.pexels.com/video/a-stressed-man-holding-his-head-7918580/"
 ],
 "d1":[
  "https://www.pexels.com/video/close-up-view-of-a-man-looking-worried-7534959/",
  "https://www.pexels.com/video/man-listening-to-someone-talk-7581218/"
 ],
 "d2":[
  "https://www.pexels.com/video/close-up-view-of-a-person-typing-7660185/",
  "https://www.pexels.com/video/close-up-shot-of-humans-hands-9465404/"
 ],
 "d3":[
  "https://www.pexels.com/video/a-person-reading-a-book-4769627/",
  "https://www.pexels.com/video/brain-27168144/",
  "https://www.pexels.com/video/a-woman-talking-to-someone-10373944/"
 ],
 "d5":[
  "https://www.pexels.com/video/brain-27168144/",
  "https://www.pexels.com/video/a-woman-talking-to-someone-10373944/",
  "https://www.pexels.com/video/man-listening-to-someone-talk-7581218/"
 ],
 "d7":[
  "https://www.pexels.com/video/a-woman-talking-to-someone-10373944/",
  "https://www.pexels.com/video/man-listening-to-someone-talk-7581218/",
  "https://www.pexels.com/video/brain-27168144/"
 ],
 "d4":[
  "https://www.pexels.com/video/woman-wearing-a-silver-watch-8995391/",
  "https://www.pexels.com/video/man-listening-to-someone-talk-7581218/"
 ],
 "t5":[
  "https://www.pexels.com/video/a-couple-holding-hands-8921925/",
  "https://www.pexels.com/video/woman-comforting-sad-twin-sister-6764083/",
  "https://www.pexels.com/video/same-sex-couple-lying-on-the-floor-holding-hands-6973129/"
 ],
 "t6":[
  "https://www.pexels.com/video/a-woman-nodding-while-talking-9034495/",
  "https://www.pexels.com/video/a-woman-touching-a-man-s-face-8088655/",
  "https://www.pexels.com/video/woman-comforting-sad-twin-sister-6764083/"
 ],
 "t7":[
  "https://www.pexels.com/video/woman-shopping-in-grocery-aisle-29846459/",
  "https://www.pexels.com/video/a-man-walking-in-a-supermarket-aisle-with-shopping-carts-16666918/",
  "https://www.pexels.com/video/shopping-aisle-perspective-on-supermarket-essentials-29376327/",
  "https://www.pexels.com/video/time-lapse-video-of-a-person-in-the-grocery-9010436/",
  "https://www.pexels.com/video/busy-supermarket-aisle-with-shoppers-35189918/",
  "https://www.pexels.com/video/a-man-walking-inside-the-supermarket-4081583/"
 ],
 "t8":[
  "https://www.pexels.com/video/close-up-shot-of-humans-hands-9465404/",
  "https://www.pexels.com/video/close-up-of-hands-touching-in-nature-30428226/",
  "https://www.pexels.com/video/a-close-up-of-a-person-s-hand-10210122/"
 ],
 "t9":[
  "https://www.pexels.com/video/a-stressed-man-holding-his-head-7918583/",
  "https://www.pexels.com/video/a-stressed-man-holding-his-head-7918580/",
  "https://www.pexels.com/video/a-man-hitting-the-wall-using-his-hand-8134591/",
  "https://www.pexels.com/video/woman-resting-her-head-on-her-hand-6382082/"
 ],
 "t10":[
  "https://www.pexels.com/video/close-up-of-hands-touching-in-nature-30428226/",
  "https://www.pexels.com/video/close-up-video-of-hands-moving-9465403/",
  "https://www.pexels.com/video/close-up-shot-of-humans-hands-9465404/"
 ]
}

def run(cmd):
 print(" ".join(map(str,cmd)),flush=True); subprocess.run(cmd,check=True)

def download(key):
 out=A/f"{key}.mp4"
 if out.exists() and out.stat().st_size>100000:return out
 pages=CANDIDATES.get(key,[SOURCES[key]])
 for page in pages:
  try:
   if out.exists():out.unlink()
   run(["yt-dlp","--no-playlist","--impersonate","chrome","--extractor-args","generic:impersonate",
        "--referer",page,"--retries","3","-f","bestvideo[height<=1920][ext=mp4]/best[height<=1920]/best",
        "--merge-output-format","mp4","-o",str(out),page])
   if out.exists() and out.stat().st_size>100000:
    time.sleep(2);return out
  except subprocess.CalledProcessError:
   time.sleep(3)
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

def overlay_story(path,b,i,total):
 im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
 gradient(im,True);gradient(im,False)
 mode=b.get("mode","center")
 d.rounded_rectangle((30,30,252,68),18,fill=(57,31,68,220))
 d.text((46,40),"relato reconstruído",font=ft(16,False),fill=WHITE)
 d.text((646,38),f"{i+1:02}",font=ft(17),fill=PALE)
 title=b["text"]
 if mode=="quote":
  d.text((42,185),"Ela disse:",font=ft(24,False),fill=PALE)
  lines(d,title,42,235,ft(60),WHITE,630,7)
  d.line((42,445,660,445),fill=ROSE,width=7)
 elif mode=="inside":
  d.rectangle((0,0,W,H),fill=(37,20,44,155))
  d.text((44,165),"Por dentro",font=ft(22,False),fill=PALE)
  if "|" in title:
   yy=215
   for segment in title.split("|"):
    d.text((44,yy),segment,font=ft(54),fill=WHITE,stroke_width=2,stroke_fill=(20,12,23,150));yy+=70
  else:
   lines(d,title,44,215,ft(58),WHITE,620,5)
  if b.get("small"):lines(d,b["small"],44,930,ft(25,False),PALE,615,5)
 elif mode=="contrast":
  d.rounded_rectangle((35,145,685,425),30,fill=(26,16,30,210))
  d.text((62,175),b.get("tag","Por fora"),font=ft(20,False),fill=PALE)
  lines(d,title,62,220,ft(54),WHITE,580,5)
  d.rounded_rectangle((35,825,685,1085),30,fill=(117,71,137,225))
  d.text((62,850),b.get("tag2","Por dentro"),font=ft(20,False),fill=WHITE)
  lines(d,b.get("small",""),62,900,ft(48),WHITE,580,5)
 elif mode=="final":
  d.rectangle((0,0,W,H),fill=(36,19,43,196))
  lines(d,title,50,250,ft(53),WHITE,620,8,True)
  if b.get("small"):
   d.rounded_rectangle((48,870,672,966),35,fill=(245,229,248,245))
   lines(d,b["small"],78,893,ft(24),DARK,565,5,True)
 else:
  y=b.get("y",230)
  lines(d,title,42,y,ft(b.get("size",56)),WHITE,630,6,b.get("center",False))
  if b.get("small"):lines(d,b["small"],42,y+220,ft(25,False),PALE,620,5)
 d.text((30,1218),"@fealemdodiagnostico",font=ft(15,False),fill=WHITE)
 d.rounded_rectangle((430,1227,690,1235),4,fill=(255,255,255,65))
 d.rounded_rectangle((430,1227,430+int(260*(i+1)/total),1235),4,fill=LILAC)
 im.save(path)

def overlay_words(path,b,i,total):
 im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
 gradient(im,True);gradient(im,False)
 mode=b.get("mode","word")
 d.text((30,33),"o que acontece antes da resposta",font=ft(16,False),fill=WHITE)
 d.text((652,33),f"{i+1:02}",font=ft(17),fill=PALE)
 text=b["text"]
 if mode=="scatter":
  d.rectangle((0,0,W,H),fill=(32,19,38,145))
  words=text.split("|")
  positions=[(42,220,-7),(285,430,5),(80,680,-3),(330,890,8)]
  for word,(x,y,a) in zip(words,positions):
   rotated_text(im,word,(x,y),48,WHITE,a)
 elif mode=="blank":
  d.rounded_rectangle((35,190,685,930),34,fill=(249,240,226,239))
  d.text((62,225),"A resposta estava aqui:",font=ft(24,False),fill=DARK)
  d.line((65,385,650,385),fill=LILAC,width=5)
  d.line((65,535,590,535),fill=LILAC,width=5)
  d.line((65,685,625,685),fill=LILAC,width=5)
  d.text((62,800),"...mas a primeira palavra não vinha.",font=ft(25),fill=ROSE)
 elif mode=="clock":
  d.rectangle((0,0,W,H),fill=(38,21,45,142))
  d.text((55,180),b.get("clock","05"),font=ft(170),fill=WHITE)
  d.text((390,300),"segundos",font=ft(30,False),fill=PALE)
  lines(d,text,48,690,ft(48),WHITE,620,6)
 elif mode=="steps":
  d.rounded_rectangle((34,160,686,1040),36,fill=(245,233,248,242))
  d.text((62,195),"Quando a pessoa travar:",font=ft(25),fill=DARK)
  yy=290
  for n,s in enumerate(text.split("|"),1):
   d.ellipse((60,yy,118,yy+58),fill=LILAC);d.text((82,yy+13),str(n),font=ft(23),fill=WHITE)
   lines(d,s,145,yy+5,ft(31),DARK,490,4);yy+=190
 elif mode=="final":
  d.rectangle((0,0,W,H),fill=(46,25,55,205))
  lines(d,text,50,245,ft(50),WHITE,620,8,True)
  if b.get("small"):lines(d,b["small"],65,860,ft(25,False),PALE,590,5,True)
 else:
  lines(d,text,40,b.get("y",240),ft(b.get("size",58)),WHITE,640,7,b.get("center",False))
  if b.get("small"):lines(d,b["small"],40,b.get("y",240)+235,ft(26,False),PALE,620,5)
 d.text((30,1218),"@fealemdodiagnostico",font=ft(15,False),fill=WHITE)
 d.rounded_rectangle((430,1227,690,1235),4,fill=(255,255,255,65))
 d.rounded_rectangle((430,1227,430+int(260*(i+1)/total),1235),4,fill=LILAC)
 im.save(path)

def render_part(src,ov,out,dur,start,style,direction):
 sat=.68 if style=="story" else .82
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
  (overlay_story if style=="story" else overlay_words)(ov,b,i,len(beats))
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
 {"src":"t7","text":"Eu estava na fila.","dur":2.4,"start":0,"size":64},
 {"src":"t8","text":"O tique começou.","small":"Discreto. Mas visível.","dur":2.5,"start":1},
 {"src":"t9","text":"A pessoa atrás de mim olhou.","dur":2.7,"start":2},
 {"src":"t7","text":"“Dá para parar?”","mode":"quote","dur":2.8,"start":4},
 {"src":"t10","text":"Eu fingi que não ouvi.","dur":2.7,"start":5},
 {"src":"t8","text":"Tentei segurar.","small":"Só para ninguém olhar de novo.","dur":2.9,"start":6},
 {"src":"t10","text":"Pescoço.|Mãos.|Respiração.|Pressão.","mode":"inside","small":"Tudo ficou mais difícil ao mesmo tempo.","dur":3.4,"start":8},
 {"src":"t2","text":"Silêncio.","mode":"contrast","tag":"Por fora","tag2":"Por dentro","small":"Meu corpo gritava.","dur":3.3,"start":9},
 {"src":"t7","text":"Quando finalmente saí...","dur":2.7,"start":10},
 {"src":"t9","text":"o tique voltou mais intenso.","mode":"inside","small":"Eu não tinha escolhido nenhum daqueles movimentos.","dur":3.5,"start":12},
 {"src":"t5","text":"Não era desrespeito.","small":"Era um corpo tentando existir sem ser vigiado.","dur":3.5,"start":0},
 {"src":"t4","text":"Acolhimento não apaga o tique.","small":"Mas pode diminuir o peso de ser julgado.","dur":3.8,"start":1},
 {"src":"t6","text":"Se você já escondeu algo para conseguir caber...","dur":3.7,"start":1,"size":48},
 {"src":"t5","text":"você conhece esse peso.","mode":"inside","dur":3.0,"start":5},
 {"src":"t4","text":"Tique não é falta de educação.","mode":"final","small":"Compartilhe. Talvez alguém pare de julgar hoje.","dur":4.4,"start":6}
]

TDL=[
 {"src":"d1","text":"Eu sabia a resposta.","dur":2.6,"start":0,"size":66},
 {"src":"d2","text":"Ela estava inteira na minha cabeça.","dur":2.9,"start":1},
 {"src":"d3","text":"Então veio a pergunta:","dur":2.4,"start":2},
 {"src":"d1","text":"“Por que isso aconteceu?”","dur":3.0,"start":4,"size":52},
 {"src":"d2","text":"Eu procurei a primeira palavra.","dur":3.0,"start":5},
 {"src":"d3","text":"A resposta estava pronta.","mode":"blank","dur":3.5,"start":6},
 {"src":"d4","text":"Ninguém disse nada.","mode":"clock","clock":"05","dur":2.7,"start":0},
 {"src":"d4","text":"A espera virou cobrança.","mode":"clock","clock":"10","dur":2.8,"start":4},
 {"src":"d1","text":"“Você não estudou?”","dur":2.8,"start":8,"size":55},
 {"src":"d2","text":"Eu estudei.","small":"O problema não era saber.","dur":2.7,"start":9},
 {"src":"d5","text":"palavras|ordem|pressão|silêncio","mode":"scatter","dur":3.5,"start":0},
 {"src":"d3","text":"Sob pressão, as palavras se desmontam.","small":"Isso não diminui a inteligência.","dur":3.7,"start":10,"size":48},
 {"src":"d2","text":"Uma pergunta|Uma pausa de verdade|Um apoio visual","mode":"steps","dur":4.7,"start":12},
 {"src":"d7","text":"Às vezes, apoiar a comunicação é parar de apressar.","dur":4.2,"start":0,"size":47},
 {"src":"d3","text":"Tempo não é incapacidade.","mode":"final","small":"Envie para quem ainda confunde uma pausa com falta de resposta.","dur":4.8,"start":14}
]

if __name__=="__main__":
 ap=argparse.ArgumentParser();ap.add_argument("--preview",action="store_true");args=ap.parse_args()
 build("Video_1_Tourette_experiencia_v4","story",TOURETTE,args.preview)
 build("Video_2_TDL_palavras_v4","words",TDL,args.preview)
