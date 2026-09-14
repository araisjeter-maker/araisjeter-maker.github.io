import math, os, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W,H,FPS=720,1280,24
CREAM=(247,237,222)
INK=(39,31,45)
LILAC=(116,82,135)
LILAC2=(179,148,194)
BLUE=(98,139,158)
WHITE=(255,255,255)

FONT_PATH="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG_PATH="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(n,bold=True): return ImageFont.truetype(FONT_PATH if bold else REG_PATH,n)

def ease(t):
    t=max(0,min(1,t))
    return 1-(1-t)**3
def lerp(a,b,t): return a+(b-a)*t
def mix(a,b,t): return tuple(int(lerp(a[i],b[i],t)) for i in range(3))
def gradient(top,bottom):
    im=Image.new("RGB",(W,H)); p=im.load()
    for y in range(H):
        c=mix(top,bottom,y/(H-1))
        for x in range(W): p[x,y]=c
    return im

BG1=gradient((71,49,83),(25,18,30))
BG2=gradient((52,72,88),(27,22,34))

def text_size(draw,text,f): return draw.textbbox((0,0),text,font=f)[2:]
def wrap(draw,text,f,maxw):
    words=text.split(); lines=[]; line=""
    for word in words:
        test=(line+" "+word).strip()
        if text_size(draw,test,f)[0]>maxw and line:
            lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    return lines[:4]

def caption(im,text,alpha=1,shift=0,pop=1,box=CREAM,color=INK):
    if not text or alpha<=0:return
    layer=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    f=font(43); lines=wrap(d,text,f,570); lh=54
    bh=len(lines)*lh+42; y=int(78+shift); rect=(55,y,W-55,y+bh)
    d.rounded_rectangle(rect,22,fill=box+(int(242*alpha),))
    for i,line in enumerate(lines):
        bb=d.textbbox((0,0),line,font=f); tw=bb[2]-bb[0]
        d.text(((W-tw)//2,y+21+i*lh),line,font=f,fill=color+(int(255*alpha),))
    if pop!=1:
        crop=layer.crop((35,y-18,W-35,y+bh+18))
        nw=max(1,int(crop.width*pop));nh=max(1,int(crop.height*pop))
        crop=crop.resize((nw,nh),Image.Resampling.LANCZOS)
        layer=Image.new("RGBA",(W,H),(0,0,0,0));layer.alpha_composite(crop,((W-nw)//2,y+(bh-nh)//2))
    im.alpha_composite(layer)

def footer(im):
    d=ImageDraw.Draw(im); f=font(17,False);t="@fealemdodiagnostico"
    w=text_size(d,t,f)[0];d.text(((W-w)//2,H-48),t,font=f,fill=(255,255,255,190))

def vignette(im):
    ov=Image.new("RGBA",(W,H),(0,0,0,0));d=ImageDraw.Draw(ov)
    d.rectangle((0,0,W,330),fill=(14,8,18,65))
    d.rectangle((0,H-180,W,H),fill=(14,8,18,45))
    im.alpha_composite(ov)

def blob_motion(im,t,colors=(LILAC2,CREAM)):
    d=ImageDraw.Draw(im,"RGBA")
    for i in range(7):
        x=W/2+math.sin(t*.7+i*1.2)*(250-i*9)
        y=H/2+math.cos(t*.5+i*1.4)*(420-i*18)
        r=75+i*12
        c=colors[i%len(colors)]
        d.ellipse((x-r,y-r,x+r,y+r),fill=c+(18,))

def draw_tourette(t):
    im=BG1.copy().convert("RGBA");blob_motion(im,t)
    d=ImageDraw.Draw(im,"RGBA")
    # Continuous tension line and pressure rings
    pts=[]
    for x in range(-20,W+20,8):
        amp=34+20*math.sin(t*.8)
        y=680+math.sin(x*.035+t*6)*amp+math.sin(x*.09-t*4)*10
        pts.append((x,y))
    d.line(pts,fill=(236,214,242,220),width=8)
    if t<4.6:
        pull=ease(min(1,t/2.5));cx=W/2
        d.line((90,870,cx-70*pull,870),fill=(245,235,218,190),width=10)
        d.line((W-90,870,cx+70*pull,870),fill=(245,235,218,190),width=10)
        d.ellipse((cx-32,838,cx+32,902),outline=(203,167,216,230),width=9)
    elif t<8:
        p=(t-4.6)/3.4;cx,cy=W/2,790
        for i in range(5):
            r=70+i*52-(math.sin(p*math.pi)*22)
            d.ellipse((cx-r,cy-r,cx+r,cy+r),outline=(223,193,232,120-i*14),width=7)
        d.rounded_rectangle((230,720,490,860),34,fill=(105,74,121,150))
    else:
        p=ease((t-8)/4);cx,cy=W/2,760
        for i in range(8):
            a=i*math.pi/4+t*.25;r=70+p*(160+i*8)
            px=cx+math.cos(a)*r;py=cy+math.sin(a)*r
            d.ellipse((px-14,py-14,px+14,py+14),fill=(245,234,217,int(210*(1-p*.45))))
        d.ellipse((cx-95-p*25,cy-95-p*25,cx+95+p*25,cy+95+p*25),fill=(181,148,195,120))
    vignette(im)
    beats=[
      (0,2.2,"MANDAR PARAR AUMENTA O ESFORÇO.",CREAM,INK,"pop"),
      (2.2,4.6,"TIQUES NÃO SÃO ESCOLHA.",(234,219,240),INK,"rise"),
      (4.6,7.6,"CONTER PODE CAUSAR TENSÃO E DESCONFORTO.",CREAM,INK,"fade"),
      (7.6,10.0,"RESPEITO REDUZ A PRESSÃO.",(220,235,239),INK,"rise"),
      (10.0,12.0,"COMPARTILHE COM QUEM PRECISA ENTENDER.",CREAM,INK,"pop")]
    for a,b,txt,box,col,kind in beats:
        if a<=t<b:
            q=ease(min(1,(t-a)/.38));shift=(1-q)*42 if kind=="rise" else 0;pop=.84+.16*q if kind=="pop" else 1
            caption(im,txt,q,shift,pop,box,col);break
    footer(im);return im.convert("RGB")

WORDS=["EU","SEI","O QUE","QUERO","DIZER"]
def draw_tdl(t):
    im=BG2.copy().convert("RGBA");blob_motion(im,t,(BLUE,LILAC2))
    d=ImageDraw.Draw(im,"RGBA")
    if t<6:
        for i,w in enumerate(WORDS):
            a=i*1.25+t*.9;x=360+math.sin(a)*235;y=670+math.cos(a*1.4)*270
            ww=118 if len(w)<4 else 160
            d.rounded_rectangle((x-ww/2,y-34,x+ww/2,y+34),16,fill=(246,236,221,220))
            f=font(23);tw=text_size(d,w,f)[0];d.text((x-tw/2,y-15),w,font=f,fill=INK+(255,))
    elif t<10:
        p=ease((t-6)/4)
        for i,w in enumerate(WORDS):
            y=560+i*88;x=lerp(80+(i%2)*390,260,p)
            d.rounded_rectangle((x,y,x+200,y+62),15,fill=(236,220,241,225))
            f=font(21);d.text((x+18,y+17),w,font=f,fill=INK+(255,))
        d.line((230,520,230,1040),fill=(211,187,220,120),width=5)
    elif t<16:
        p=(t-10)/6;cx,cy=360,760
        d.ellipse((cx-125,cy-125,cx+125,cy+125),outline=(244,234,218,220),width=12)
        ang=-math.pi/2+p*math.pi*2
        d.line((cx,cy,cx+math.cos(ang)*92,cy+math.sin(ang)*92),fill=(191,154,205,240),width=12)
        for i in range(3):
            y=980+i*74
            d.rounded_rectangle((125,y,595,y+52),14,fill=(244,234,218,150+i*25))
    elif t<22:
        p=ease((t-16)/6)
        labels=["UMA PERGUNTA","UMA PAUSA","UM APOIO VISUAL"]
        for i,w in enumerate(labels):
            y=560+i*150;x=int(lerp(-430,105,p if i==0 else max(0,min(1,p-.12*i))*1.25))
            d.rounded_rectangle((x,y,x+510,y+92),24,fill=((245,234,218,230) if i!=1 else (229,214,236,235)))
            f=font(27);d.text((x+28,y+29),w,font=f,fill=INK+(255,))
    else:
        p=ease((t-22)/4);cx,cy=360,760
        for i in range(12):
            a=i*math.pi/6;tow=90+p*250
            px=cx+math.cos(a)*tow;py=cy+math.sin(a)*tow
            d.ellipse((px-12,py-12,px+12,py+12),fill=(245,234,218,200))
        d.rounded_rectangle((145,650,575,850),36,fill=(112,80,130,190))
        f=font(35);d.text((220,718),"ENTENDI",font=f,fill=WHITE+(255,))
    vignette(im)
    beats=[
      (0,2.7,"ELA SABE A RESPOSTA.",CREAM,INK,"pop"),
      (2.7,5.7,"MAS A FRASE NÃO CHEGA.",(233,217,239),INK,"rise"),
      (5.7,9.7,"TDL NÃO É FALTA DE INTELIGÊNCIA.",CREAM,INK,"fade"),
      (9.7,12.6,"DÊ TEMPO.",(220,235,239),INK,"pop"),
      (12.6,16.2,"USE APOIO VISUAL.",CREAM,INK,"rise"),
      (16.2,20.1,"FAÇA UMA PERGUNTA POR VEZ.",(233,217,239),INK,"rise"),
      (20.1,23.3,"COMUNICAÇÃO TAMBÉM PRECISA DE ESPAÇO.",CREAM,INK,"fade"),
      (23.3,26.0,"SALVE PARA LEMBRAR.",(220,235,239),INK,"pop")]
    for a,b,txt,box,col,kind in beats:
        if a<=t<b:
            q=ease(min(1,(t-a)/.4));shift=(1-q)*42 if kind=="rise" else 0;pop=.84+.16*q if kind=="pop" else 1
            caption(im,txt,q,shift,pop,box,col);break
    footer(im);return im.convert("RGB")

def render(name,duration,fn):
    os.makedirs("videos",exist_ok=True)
    cmd=["ffmpeg","-y","-f","rawvideo","-vcodec","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-vf","scale=1080:1920:flags=lanczos","-c:v","libx264","-preset","medium","-crf","18","-pix_fmt","yuv420p","-movflags","+faststart",f"videos/{name}.mp4"]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for n in range(int(duration*FPS)):
        p.stdin.write(fn(n/FPS).tobytes())
    p.stdin.close()
    if p.wait()!=0: raise SystemExit("Falha na renderização")

if __name__=="__main__":
    render("Video_1_Tourette_profissional",12,draw_tourette)
    render("Video_2_TDL_profissional",26,draw_tdl)
