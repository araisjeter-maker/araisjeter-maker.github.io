import os, subprocess, urllib.request
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W,H,FPS=1080,1920,30
ROOT=Path(__file__).parent
A=ROOT/"assets_v2"; O=ROOT/"overlays_v2"; P=ROOT/"parts_v2"; V=ROOT/"videos"
for d in (A,O,P,V): d.mkdir(exist_ok=True)

BOLD="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK=(39,31,44,255); CREAM=(248,239,224,247); LILAC=(119,76,139,255)
PALE=(227,207,234,255); WHITE=(255,255,255,255); RED=(156,66,80,255)

SOURCES={
 "t_stress":("pexels","https://www.pexels.com/video/man-sitting-on-sofa-holding-his-head-7918624/"),
 "t_hands":("pexels","https://www.pexels.com/video/a-woman-massaging-her-hand-8116796/"),
 "t_support":("pexels","https://www.pexels.com/video/people-holding-each-other-s-hands-7522355/"),
 "t_breathe":("pexels","https://www.pexels.com/video/an-elderly-man-s-hand-on-chest-and-belly-while-deep-breathing-8795151/"),
 "d_write":("mixkit","https://mixkit.co/free-stock-video/close-up-a-hand-writing-notes-on-a-notebook-with-99890/"),
 "d_type":("mixkit","https://mixkit.co/free-stock-video/person-typing-on-a-computer-in-detail-4907/"),
 "d_clock":("pexels","https://www.pexels.com/video/a-ticking-clock-7033786/"),
 "d_sticky":("mixkit","https://mixkit.co/free-stock-video/student-hand-takes-a-stiky-note-to-paste-it-on-50112/"),
 "d_list":("mixkit","https://mixkit.co/free-stock-video/close-up-of-a-hand-writing-to-do-list-on-99909/")
}

def run(cmd):
    print(" ".join(map(str,cmd)))
    subprocess.run(cmd,check=True)

def download(key):
    provider,page=SOURCES[key]; out=A/f"{key}.mp4"
    if out.exists() and out.stat().st_size>100000:return out
    try:
        run(["yt-dlp","--no-playlist","--referer",page,"--merge-output-format","mp4",
             "-f","bestvideo[height<=1920]+bestaudio/best[height<=1920]/best",
             "-o",str(out),page])
        if out.exists() and out.stat().st_size>100000:return out
    except Exception as e: print("yt-dlp falhou",e)
    # Fallback dos clipes Mixkit já validados.
    fallbacks={
      "t_stress":"https://mixkit.co/free-stock-video/worried-and-sad-man-with-his-head-down-4701/",
      "t_hands":"https://mixkit.co/free-stock-video/hands-of-a-wedding-couple-she-comforts-him-8754/",
      "t_support":"https://mixkit.co/free-stock-video/hands-of-a-wedding-couple-she-comforts-him-8754/",
      "t_breathe":"https://mixkit.co/free-stock-video/view-from-above-of-the-shore-of-a-beach-51503/",
      "d_clock":"https://mixkit.co/free-stock-video/view-from-above-of-the-shore-of-a-beach-51503/"
    }
    if key in fallbacks:
        page=fallbacks[key]
        run(["yt-dlp","--no-playlist","--referer",page,"-f","best[ext=mp4]/best","-o",str(out),page])
        if out.exists() and out.stat().st_size>100000:return out
    raise RuntimeError("Falha ao baixar "+key)

def font(n,b=True): return ImageFont.truetype(BOLD if b else REG,n)

def wrap(draw,text,f,maxw):
    lines=[]; cur=""
    for word in text.split():
        test=(cur+" "+word).strip()
        if cur and draw.textbbox((0,0),test,font=f)[2]>maxw:
            lines.append(cur); cur=word
        else:cur=test
    if cur:lines.append(cur)
    return lines

def centered(draw,text,y,f,fill):
    box=draw.textbbox((0,0),text,font=f); draw.text(((W-(box[2]-box[0]))//2,y),text,font=f,fill=fill)

def overlay(path,series,text,sub,kind,index,total,accent=""):
    im=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,500),fill=(21,13,26,112))
    d.rectangle((0,H-300,W,H),fill=(18,10,22,80))
    # Small native series tag
    d.rounded_rectangle((54,60,54+min(650,44+len(series)*18),116),28,fill=(91,55,108,232))
    d.text((82,74),series,font=font(23),fill=WHITE)

    if kind=="comment":
        d.rounded_rectangle((54,150,W-54,438),36,fill=(255,255,255,248))
        d.ellipse((82,184,148,250),fill=(224,205,232,255))
        d.text((103,199),"!",font=font(30),fill=LILAC)
        d.text((172,180),"comentário que machuca:",font=font(25,False),fill=(100,89,104,255))
        q=font(55)
        lines=wrap(d,"“"+text+"”",q,790); y=230
        for line in lines:
            d.text((172,y),line,font=q,fill=RED);y+=70
    elif kind=="truth":
        d.rounded_rectangle((54,150,W-54,418),36,fill=CREAM)
        d.rounded_rectangle((82,178,268,226),24,fill=LILAC)
        d.text((111,188),"O FATO",font=font(22),fill=WHITE)
        f=font(57); lines=wrap(d,text,f,850); y=252
        for line in lines:
            centered(d,line,y,f,INK);y+=70
    elif kind=="pause":
        d.rounded_rectangle((54,150,W-54,430),36,fill=CREAM)
        centered(d,"•••",172,font(58),LILAC)
        f=font(56);lines=wrap(d,text,f,850);y=258
        for line in lines:centered(d,line,y,f,INK);y+=69
    elif kind=="steps":
        d.rounded_rectangle((54,150,W-54,482),36,fill=CREAM)
        f=font(47); y=190
        for n,line in enumerate(text.split("|"),1):
            d.ellipse((86,y+6,138,y+58),fill=LILAC)
            centered_num=font(25); nb=d.textbbox((0,0),str(n),font=centered_num)
            d.text((112-(nb[2]-nb[0])/2,y+16),str(n),font=centered_num,fill=WHITE)
            d.text((166,y+4),line.strip(),font=f,fill=INK); y+=88
    else:
        d.rounded_rectangle((54,150,W-54,430),36,fill=CREAM)
        f=font(58);lines=wrap(d,text,f,850);y=194+(2-len(lines))*24
        for line in lines:centered(d,line,y,f,INK);y+=72
        if accent:
            af=font(27)
            ab=d.textbbox((0,0),accent,font=af); aw=ab[2]-ab[0]
            d.rounded_rectangle(((W-aw)//2-26,360,(W+aw)//2+26,414),27,fill=PALE)
            centered(d,accent,370,af,LILAC)
    if sub:
        sf=font(29)
        sb=d.textbbox((0,0),sub,font=sf);sw=sb[2]-sb[0]
        d.rounded_rectangle(((W-sw)//2-32,H-236,(W+sw)//2+32,H-170),30,fill=(98,61,116,232))
        centered(d,sub,H-220,sf,WHITE)
    # Story progress
    gap=10; bw=(W-108-gap*(total-1))//total
    for i in range(total):
        fill=PALE if i<=index else (255,255,255,85)
        x=54+i*(bw+gap);d.rounded_rectangle((x,H-116,x+bw,H-103),7,fill=fill)
    d.text((54,H-78),"@fealemdodiagnostico",font=font(22,False),fill=(255,255,255,225))
    im.save(path)

def part(src,out,ov,dur,start,bias,sat,tempo=1.0):
    # Continuous motion plus quick first-frame punch; crop protects the text/subject.
    x=f"(iw-ow)*(0.5+0.055*sin(t*1.15)+({bias})*0.16)"
    filt=(f"[0:v]setpts=PTS/{tempo},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H}:x='{x}':y='(ih-oh)/2',fps={FPS},"
          f"eq=contrast=1.10:saturation={sat}:brightness=-0.03,"
          "unsharp=5:5:0.45,format=yuv420p[bg];"
          f"[1:v]format=rgba,fade=t=in:st=0:d=0.12:alpha=1,"
          f"fade=t=out:st={max(.1,dur-.12):.2f}:d=.12:alpha=1[tx];"
          "[bg][tx]overlay=0:0:format=auto[v]")
    run(["ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",str(start),"-i",str(src),
         "-loop","1","-i",str(ov),"-t",str(dur),"-filter_complex",filt,
         "-map","[v]","-an","-c:v","libx264","-preset","fast","-crf","18",
         "-pix_fmt","yuv420p","-movflags","+faststart",str(out)])

def render(name,series,beats):
    parts=[]
    for i,b in enumerate(beats):
        key,text,sub,kind,dur,start,bias,sat,tempo,accent=b
        src=download(key);ov=O/f"{name}_{i:02}.png";pt=P/f"{name}_{i:02}.mp4"
        overlay(ov,series,text,sub,kind,i,len(beats),accent)
        part(src,pt,ov,dur,start,bias,sat,tempo);parts.append(pt)
    lst=P/f"{name}.txt";lst.write_text("".join(f"file '{x.resolve()}'\n" for x in parts))
    out=V/f"{name}.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(lst),
         "-an","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",
         "-movflags","+faststart",str(out)])
    run(["ffprobe","-v","error","-show_entries","stream=width,height,codec_name:format=duration",
         "-of","default=noprint_wrappers=1",str(out)])

TOURETTE=[
 ("t_stress","Para com isso.","", "comment",1.25,0,-.55,.70,1.18,""),
 ("t_hands","Eu tentei.","Não funcionou","normal",1.35,0,.55,.78,1.12,""),
 ("t_stress","O esforço virou tensão.","", "normal",1.75,2,.45,.66,1.08,"NO CORPO TODO"),
 ("t_hands","E o tique voltou.","Mais forte","normal",1.55,3,-.5,.72,1.14,""),
 ("t_stress","Tique não é escolha.","", "truth",2.10,5,-.4,.68,1.03,""),
 ("t_support","Cobrança aumenta a pressão.","Acolhimento reduz","normal",2.15,0,.5,.82,1.05,""),
 ("t_breathe","Não diga “é só parar”.","Envie para quem precisa entender","truth",3.60,1,0,.82,1.00,""),
]

TDL=[
 ("d_type","Ela respondeu errado.","Mas não era a resposta dela","normal",2.45,0,-.45,.80,1.12,""),
 ("d_clock","A pergunta veio depressa.","", "normal",2.60,0,.3,.70,1.20,""),
 ("d_write","Ela sabia.","A frase ainda não chegou","normal",2.35,0,.5,.84,1.06,""),
 ("d_type","Perguntaram novamente.","", "comment",2.55,4,.45,.72,1.18,""),
 ("d_clock","A pressão aumentou.","E as palavras sumiram","normal",2.70,2,-.3,.66,1.25,""),
 ("d_sticky","TDL não reduz inteligência.","", "truth",3.20,0,.5,.84,1.05,""),
 ("d_list","Uma pergunta|Uma pausa|Um apoio visual","Faça assim","steps",4.25,0,-.4,.88,1.04,""),
 ("d_write","Antes de dizer “fala logo”...","Salve este vídeo","pause",3.90,4,.4,.82,1.02,""),
 ("d_sticky","Dê espaço para a resposta.","Compartilhe com alguém","truth",3.15,5,-.5,.86,1.04,""),
]

if __name__=="__main__":
    render("Video_1_Tourette_viral_10x10","TOURETTE • HISTÓRIA REAL",TOURETTE)
    render("Video_2_TDL_viral_10x10","TDL • POR DENTRO DA RESPOSTA",TDL)
