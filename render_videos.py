import os, subprocess, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=1080,1920,30
ROOT=Path(__file__).parent
ASSET_DIR=ROOT/"assets_stock"
OVERLAY_DIR=ROOT/"overlays"
PART_DIR=ROOT/"parts"
VIDEO_DIR=ROOT/"videos"
for d in (ASSET_DIR,OVERLAY_DIR,PART_DIR,VIDEO_DIR): d.mkdir(exist_ok=True)

FONT_BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
CREAM=(248,239,224,246)
INK=(36,29,41,255)
LILAC=(125,82,145,255)
SOFT=(213,187,222,255)
WHITE=(255,255,255,255)

ASSETS={
 "tensao":("mixkit-hands-of-a-wedding-couple-she-comforts-him-8754", "https://mixkit.co/free-stock-video/hands-of-a-wedding-couple-she-comforts-him-8754/"),
 "pressao":("mixkit-worried-and-sad-man-with-his-head-down-4701", "https://mixkit.co/free-stock-video/worried-and-sad-man-with-his-head-down-4701/"),
 "respiro":("mixkit-view-from-above-of-the-shore-of-a-beach-51503", "https://mixkit.co/free-stock-video/view-from-above-of-the-shore-of-a-beach-51503/"),
 "escrita":("mixkit-close-up-a-hand-writing-notes-on-a-notebook-with-99890", "https://mixkit.co/free-stock-video/close-up-a-hand-writing-notes-on-a-notebook-with-99890/"),
 "lista":("mixkit-close-up-of-a-hand-writing-to-do-list-on-a-yellow-paper-notebook-99909", "https://mixkit.co/free-stock-video/close-up-of-a-hand-writing-to-do-list-on-99909/"),
 "apoio":("mixkit-student-hand-takes-a-stiky-note-to-paste-it-on-the-notebook-50112", "https://mixkit.co/free-stock-video/student-hand-takes-a-stiky-note-to-paste-it-on-50112/"),
 "teclado":("mixkit-person-typing-on-a-computer-in-detail-4907", "https://mixkit.co/free-stock-video/person-typing-on-a-computer-in-detail-4907/")
}

def run(cmd):
    print(" ".join(str(x) for x in cmd))
    subprocess.run(cmd,check=True)

def download_asset(key):
    stem,_=ASSETS[key]; dest=ASSET_DIR/f"{key}.mp4"
    if dest.exists() and dest.stat().st_size>100000: return dest
    urls=[
      f"https://assets.mixkit.co/videos/preview/{stem}-large.mp4",
      f"https://assets.mixkit.co/videos/preview/{stem}-medium.mp4",
      f"https://assets.mixkit.co/videos/preview/{stem}-small.mp4",
    ]
    for url in urls:
        try:
            req=urllib.request.Request(url,headers={
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
                "Referer":"https://mixkit.co/",
                "Origin":"https://mixkit.co",
                "Accept":"video/avif,video/webm,video/apng,video/*,*/*;q=0.8",
                "Accept-Language":"pt-BR,pt;q=0.9,en;q=0.7"
            })
            with urllib.request.urlopen(req,timeout=90) as r, open(dest,"wb") as f:
                f.write(r.read())
            if dest.stat().st_size>100000:
                print("Baixado",key,url,dest.stat().st_size); return dest
        except Exception as e:
            print("Falhou",url,e)
            if dest.exists(): dest.unlink()
    raise RuntimeError(f"Não foi possível baixar o clipe gratuito: {key}")

def fnt(size,bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG,size)

def wrap(draw,text,font,max_width):
    words=text.split(); lines=[]; current=""
    for word in words:
        trial=(current+" "+word).strip()
        if current and draw.textbbox((0,0),trial,font=font)[2]>max_width:
            lines.append(current); current=word
        else: current=trial
    if current: lines.append(current)
    return lines

def overlay_png(path,kicker,text,cta,idx,total,accent_word=None):
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    # Cinematic vignette and brand tint.
    d.rectangle((0,0,W,390),fill=(22,13,27,105))
    d.rectangle((0,H-310,W,H),fill=(18,11,22,80))
    # Native reel label.
    d.rounded_rectangle((56,70,506,126),radius=28,fill=(111,71,130,225))
    d.text((84,82),kicker,font=fnt(25),fill=WHITE)
    # Main editorial card.
    main=fnt(58)
    lines=wrap(d,text,main,888)
    line_h=72; card_h=72+line_h*len(lines)
    d.rounded_rectangle((56,154,W-56,154+card_h),radius=34,fill=CREAM)
    y=188
    for line in lines:
        box=d.textbbox((0,0),line,font=main); tw=box[2]
        d.text(((W-tw)//2,y),line,font=main,fill=INK)
        y+=line_h
    # Accent slash and retention counter.
    d.rounded_rectangle((56,154,68,154+card_h),radius=6,fill=LILAC)
    if cta:
        cfont=fnt(30)
        cbox=d.textbbox((0,0),cta,font=cfont); cw=cbox[2]
        d.rounded_rectangle(((W-cw)//2-30,H-224,(W+cw)//2+30,H-162),radius=27,fill=(112,75,130,220))
        d.text(((W-cw)//2,H-210),cta,font=cfont,fill=WHITE)
    # Progress: fast visual rhythm, safe UI area.
    gap=12; bar_w=(W-112-gap*(total-1))//total
    for n in range(total):
        color=SOFT if n<=idx else (255,255,255,100)
        x=56+n*(bar_w+gap)
        d.rounded_rectangle((x,H-116,x+bar_w,H-104),radius=6,fill=color)
    d.text((56,H-82),"@fealemdodiagnostico",font=fnt(22,False),fill=(255,255,255,220))
    im.save(path)

def make_part(source,out,overlay,duration,start,bias,grade):
    xexpr=f"(iw-ow)*(0.5+0.07*sin(t*0.9)+({bias})*0.16)"
    filt=(
      f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
      f"crop={W}:{H}:x='{xexpr}':y='(ih-oh)/2',fps={FPS},"
      f"eq=contrast=1.08:saturation={grade}:brightness=-0.035,"
      "unsharp=5:5:0.35:3:3:0.0,format=yuv420p[base];"
      f"[1:v]format=rgba,fade=t=in:st=0:d=0.16:alpha=1,"
      f"fade=t=out:st={max(0.1,duration-0.14):.2f}:d=0.14:alpha=1[txt];"
      "[base][txt]overlay=0:0:format=auto[v]"
    )
    run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",str(start),"-i",str(source),
         "-loop","1","-i",str(overlay),"-t",str(duration),"-filter_complex",filt,
         "-map","[v]","-an","-r",str(FPS),"-c:v","libx264","-preset","fast","-crf","19",
         "-pix_fmt","yuv420p",str(out)])

def render(name,kicker,beats):
    parts=[]
    for i,b in enumerate(beats):
        key,text,cta,duration,start,bias,grade=b
        source=download_asset(key)
        ov=OVERLAY_DIR/f"{name}_{i:02d}.png"
        part=PART_DIR/f"{name}_{i:02d}.mp4"
        overlay_png(ov,kicker,text,cta,i,len(beats))
        make_part(source,part,ov,duration,start,bias,grade)
        parts.append(part)
    lst=PART_DIR/f"{name}.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts),encoding="utf-8")
    out=VIDEO_DIR/f"{name}.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),
         "-an","-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(out)])
    run(["ffprobe","-v","error","-show_entries","stream=width,height,codec_name:format=duration",
         "-of","default=noprint_wrappers=1",str(out)])

TOURETTE=[
 ("pressao","MANDAR PARAR NÃO FAZ O TIQUE SUMIR.","",2.10,0.2,-0.7,0.72),
 ("tensao","SÓ AUMENTA O ESFORÇO PARA CONTER.","LEIA ATÉ O FIM",2.15,0.0,0.6,0.76),
 ("pressao","TIQUES NÃO SÃO ESCOLHA.","",2.05,3.0,0.5,0.68),
 ("tensao","ACOLHIMENTO REDUZ A PRESSÃO.","ISSO MUDA TUDO",2.25,4.2,-0.5,0.82),
 ("respiro","RESPEITE. NÃO MANDE PARAR.","COMPARTILHE",3.45,5.0,0.0,0.78),
]

TDL=[
 ("escrita","ELA SABE O QUE QUER DIZER.","",3.25,0.0,-0.5,0.82),
 ("teclado","MAS AS PALAVRAS PODEM DEMORAR.","NÃO É DESATENÇÃO",3.45,1.0,0.6,0.74),
 ("lista","TDL NÃO É FALTA DE INTELIGÊNCIA.","",3.60,0.6,-0.6,0.80),
 ("apoio","FAÇA UMA PERGUNTA POR VEZ.","DICA PRÁTICA",3.65,0.0,0.5,0.84),
 ("escrita","DÊ TEMPO PARA A RESPOSTA.","ESPERE",3.45,4.2,0.5,0.76),
 ("apoio","USE IMAGENS, GESTOS E PALAVRAS-CHAVE.","FACILITE",4.15,4.6,-0.5,0.88),
 ("lista","COMUNICAÇÃO TAMBÉM PRECISA DE ESPAÇO.","SALVE E ENVIE",4.45,4.7,0.4,0.82),
]

if __name__=="__main__":
    render("Video_1_Tourette_profissional","TOURETTE • NÃO É ESCOLHA",TOURETTE)
    render("Video_2_TDL_profissional","TDL • COMUNICAÇÃO",TDL)
