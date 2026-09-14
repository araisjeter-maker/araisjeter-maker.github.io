import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# Editor 100% gratuito: Python + Pillow + FFmpeg + vídeos Pexels gratuitos.
# Dois formatos visuais independentes, sem áudio e sem cenas reaproveitadas dos vídeos anteriores.
BW, BH, FPS = 720, 1280, 30
OW, OH = 1080, 1920
ROOT = Path(__file__).parent
ASSETS = ROOT / "assets_v3"
OVERLAYS = ROOT / "overlays_v3"
PARTS = ROOT / "parts_v3"
VIDEOS = ROOT / "videos"
for folder in (ASSETS, OVERLAYS, PARTS, VIDEOS):
    folder.mkdir(exist_ok=True)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
INK = (34, 25, 38, 255)
WHITE = (255, 255, 255, 255)
CREAM = (250, 241, 225, 255)
LILAC = (126, 79, 148, 255)
LILAC_DARK = (77, 43, 91, 255)
LILAC_PALE = (232, 216, 238, 255)
ROSE = (181, 73, 97, 255)
GREEN = (66, 119, 102, 255)

SOURCES = {
    # Tourette — conjunto exclusivo
    "t_hands": "https://www.pexels.com/video/an-anxious-patient-rubbing-her-hands-6010758/",
    "t_sofa": "https://www.pexels.com/video/a-stressed-man-sitting-on-a-sofa-11945234/",
    "t_pressure": "https://www.pexels.com/video/a-distressed-woman-screaming-4587899/",
    "t_support": "https://www.pexels.com/video/a-person-comforting-someone-while-touching-back-8555708/",
    "t_release": "https://www.pexels.com/video/a-woman-having-a-body-massage-5894177/",
    # TDL — conjunto exclusivo e diferente
    "d_phone": "https://www.pexels.com/video/woman-texting-on-her-phone-8142388/",
    "d_message": "https://www.pexels.com/video/person-texting-a-message-7362704/",
    "d_wait": "https://www.pexels.com/video/a-bored-girl-waiting-with-a-big-alarm-clock-besides-her-7346135/",
    "d_clock": "https://www.pexels.com/video/a-person-with-a-wall-clock-on-the-head-is-sitting-on-the-couch-8322040/",
    "d_write": "https://www.pexels.com/video/close-up-of-hand-writing-in-notebook-31948465/",
}

def run(cmd):
    print(" ".join(map(str, cmd)), flush=True)
    subprocess.run(cmd, check=True)

def download(key):
    target = ASSETS / f"{key}.mp4"
    if target.exists() and target.stat().st_size > 100000:
        return target
    page = SOURCES[key]
    cmd = [
        "yt-dlp", "--no-playlist", "--impersonate", "chrome",
        "--extractor-args", "generic:impersonate",
        "--referer", page,
        "-f", "bestvideo[height<=1920][ext=mp4]/best[height<=1920][ext=mp4]/best[height<=1920]/best",
        "--merge-output-format", "mp4", "-o", str(target), page
    ]
    run(cmd)
    if not target.exists() or target.stat().st_size <= 100000:
        raise RuntimeError(f"Download gratuito falhou: {key}")
    return target

def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, size)

def text_width(draw, text, f):
    box = draw.textbbox((0, 0), text, font=f)
    return box[2] - box[0]

def wrap(draw, text, f, max_width):
    lines, current = [], ""
    for word in text.split():
        candidate = (current + " " + word).strip()
        if current and text_width(draw, candidate, f) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines

def draw_lines(draw, text, xy, f, fill, max_width, spacing=8, center=False):
    x, y = xy
    lines = wrap(draw, text, f, max_width)
    for line in lines:
        xx = (BW - text_width(draw, line, f)) // 2 if center else x
        draw.text((xx, y), line, font=f, fill=fill)
        y += f.size + spacing
    return y

def brand(draw, label, step, total, dark=False):
    color = WHITE if dark else LILAC_DARK
    draw.rounded_rectangle((28, 28, 254, 68), 20, fill=(67, 39, 79, 220))
    draw.text((45, 39), label, font=font(17), fill=WHITE)
    draw.text((28, 1223), "@fealemdodiagnostico", font=font(16, False), fill=color)
    usable = 250
    draw.rounded_rectangle((442, 1231, 692, 1238), 4, fill=(255,255,255,90) if dark else (91,54,108,65))
    draw.rounded_rectangle((442, 1231, 442 + int(usable*(step+1)/total), 1238), 4, fill=LILAC_PALE if dark else LILAC)

def documentary_overlay(path, beat, step, total):
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    kind, title, sub = beat["kind"], beat["title"], beat.get("sub", "")
    # Cinematic gradients keep text readable without repeating the old beige card formula.
    d.rectangle((0, 0, BW, 250), fill=(14, 8, 17, 150))
    d.rectangle((0, 970, BW, BH), fill=(13, 7, 16, 125))
    brand(d, "RELATO • TOURETTE", step, total, dark=True)

    if kind == "comment":
        d.rounded_rectangle((32, 112, 688, 302), 28, fill=(255,255,255,248))
        d.ellipse((55, 140, 101, 186), fill=LILAC_PALE)
        d.text((70, 149), "!", font=font(23), fill=LILAC_DARK)
        d.text((120, 137), "o comentário chega primeiro:", font=font(17,False), fill=(103,92,107,255))
        draw_lines(d, "“" + title + "”", (120, 178), font(42), ROSE, 520, 4)
        d.text((40, 340), sub, font=font(20), fill=WHITE)
    elif kind == "editorial":
        d.rectangle((0, 126, BW, 410), fill=(54, 30, 64, 218))
        d.text((38, 150), "POR DENTRO", font=font(18), fill=LILAC_PALE)
        draw_lines(d, title.upper(), (38, 190), font(62), WHITE, 640, 2)
        if sub:
            d.rounded_rectangle((38, 386, 570, 442), 25, fill=(250,241,225,238))
            d.text((60, 401), sub, font=font(23), fill=INK)
    elif kind == "counter":
        d.rounded_rectangle((30, 124, 194, 174), 22, fill=ROSE)
        d.text((52, 138), "NÃO É ESCOLHA", font=font(16), fill=WHITE)
        draw_lines(d, title, (38, 205), font(49), WHITE, 640, 5)
        d.line((38, 388, 600, 388), fill=LILAC_PALE, width=5)
        draw_lines(d, sub, (38, 410), font(25,False), WHITE, 630, 5)
    elif kind == "fact":
        d.rounded_rectangle((34, 130, 686, 455), 34, fill=(250,241,225,246))
        d.text((62, 158), "O QUE QUASE NINGUÉM VÊ", font=font(17), fill=LILAC)
        draw_lines(d, title, (62, 205), font(45), INK, 590, 6)
        if sub:
            d.rounded_rectangle((62, 368, 645, 426), 25, fill=LILAC_PALE)
            d.text((82, 384), sub, font=font(22), fill=LILAC_DARK)
    elif kind == "contrast":
        d.rounded_rectangle((32, 128, 688, 472), 32, fill=(31,20,35,232))
        d.text((60, 154), "TROQUE ISTO", font=font(18), fill=(244,158,173,255))
        draw_lines(d, title, (60, 198), font(38), WHITE, 590, 5)
        d.line((60, 302, 655, 302), fill=(255,255,255,80), width=2)
        d.text((60, 326), "POR ISTO", font=font(18), fill=(161,224,203,255))
        draw_lines(d, sub, (60, 370), font(36), WHITE, 590, 5)
    elif kind == "cta":
        d.rounded_rectangle((32, 126, 688, 494), 34, fill=(250,241,225,248))
        d.text((60, 156), "ANTES DE JULGAR", font=font(19), fill=ROSE)
        draw_lines(d, title, (60, 210), font(49), INK, 590, 5)
        d.rounded_rectangle((60, 400, 642, 462), 28, fill=LILAC)
        d.text((88, 417), sub, font=font(23), fill=WHITE)
    im.save(path)

def bubble(draw, x, y, w, text, mine=False, dim=False):
    fill = (126,79,148,245) if mine else (255,255,255,247)
    if dim:
        fill = (100,91,104,218)
    color = WHITE if mine or dim else INK
    f = font(24, False)
    lines = wrap(draw, text, f, w-34)
    h = 30 + len(lines)*31
    draw.rounded_rectangle((x, y, x+w, y+h), 23, fill=fill)
    yy = y+15
    for line in lines:
        draw.text((x+17, yy), line, font=f, fill=color)
        yy += 31
    return y+h

def chat_overlay(path, beat, step, total):
    im = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # TDL has its own visual language: a conversation/interface, never a documentary card.
    d.rectangle((0, 0, BW, BH), fill=(31,20,35,88))
    d.rounded_rectangle((24, 82, 696, 1158), 36, fill=(242,234,244,238))
    d.rounded_rectangle((24, 82, 696, 160), 36, fill=(78,45,92,252))
    d.rectangle((24, 128, 696, 160), fill=(78,45,92,252))
    d.ellipse((48, 101, 92, 145), fill=LILAC_PALE)
    d.text((63, 109), "T", font=font(20), fill=LILAC_DARK)
    d.text((108, 99), "por dentro da resposta", font=font(22), fill=WHITE)
    d.text((108, 128), "TDL • conversa simulada", font=font(14,False), fill=(227,207,234,255))
    d.text((624, 108), f"{step+1:02}", font=font(18), fill=WHITE)

    y = 198
    for message in beat.get("messages", []):
        side, txt = message
        if side == "them":
            y = bubble(d, 54, y, 475, txt, False) + 18
        elif side == "me":
            y = bubble(d, 190, y, 474, txt, True) + 18
        elif side == "dim":
            y = bubble(d, 54, y, 540, txt, False, True) + 18
        elif side == "typing":
            d.rounded_rectangle((54,y,170,y+58),24,fill=(255,255,255,247))
            for xx in (80,111,142):
                d.ellipse((xx,y+24,xx+10,y+34),fill=(126,79,148,220))
            y += 76

    if beat.get("timer"):
        d.rounded_rectangle((245, y+5, 475, y+61), 25, fill=(255,255,255,220))
        d.text((274, y+20), beat["timer"], font=font(20), fill=ROSE)
        y += 86

    if beat.get("insight"):
        d.rounded_rectangle((48, max(y+10, 750), 672, 1044), 30, fill=(250,241,225,250))
        d.text((76, max(y+38, 778)), beat.get("label","O QUE ACONTECE"), font=font(16), fill=LILAC)
        draw_lines(d, beat["insight"], (76, max(y+80, 820)), font(34), INK, 565, 5)
        if beat.get("sub"):
            d.text((76, 996), beat["sub"], font=font(19,False), fill=LILAC_DARK)

    if beat.get("steps"):
        sy = 754
        for n, txt in enumerate(beat["steps"], 1):
            d.ellipse((60, sy, 108, sy+48), fill=LILAC)
            d.text((77, sy+10), str(n), font=font(20), fill=WHITE)
            d.rounded_rectangle((122, sy-4, 656, sy+54), 22, fill=(255,255,255,245))
            d.text((145, sy+11), txt, font=font(23), fill=INK)
            sy += 78

    brand(d, "TDL • CONVERSA", step, total, dark=False)
    im.save(path)

def render_part(src, overlay, out, duration, start, style, bias=0.0):
    if style == "doc":
        color = "eq=contrast=1.14:saturation=0.72:brightness=-0.045,unsharp=5:5:0.45"
    else:
        color = "eq=contrast=1.06:saturation=0.84:brightness=-0.015,gblur=sigma=0.35"
    xexpr = f"(iw-ow)*(0.5+0.045*sin(t*0.9)+({bias})*0.15)"
    vf = (
        f"[0:v]scale={BW}:{BH}:force_original_aspect_ratio=increase,"
        f"crop={BW}:{BH}:x='{xexpr}':y='(ih-oh)/2',fps={FPS},{color},format=yuv420p[bg];"
        f"[1:v]format=rgba,fade=t=in:st=0:d=0.10:alpha=1,"
        f"fade=t=out:st={max(.1,duration-.10):.2f}:d=0.10:alpha=1[tx];"
        "[bg][tx]overlay=0:0:format=auto[v]"
    )
    run([
        "ffmpeg","-y","-loglevel","error","-stream_loop","-1","-ss",str(start),"-i",str(src),
        "-loop","1","-i",str(overlay),"-t",str(duration),"-filter_complex",vf,
        "-map","[v]","-an","-c:v","libx264","-preset","fast","-crf","18",
        "-pix_fmt","yuv420p",str(out)
    ])

def assemble(name, style, beats):
    clips = []
    for i, beat in enumerate(beats):
        src = download(beat["src"])
        ov = OVERLAYS / f"{name}_{i:02}.png"
        part = PARTS / f"{name}_{i:02}.mp4"
        if style == "doc":
            documentary_overlay(ov, beat, i, len(beats))
        else:
            chat_overlay(ov, beat, i, len(beats))
        render_part(src, ov, part, beat["dur"], beat.get("start",0), style, beat.get("bias",0))
        clips.append(part)
    listing = PARTS / f"{name}.txt"
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in clips))
    temp = PARTS / f"{name}_base.mp4"
    output = VIDEOS / f"{name}.mp4"
    run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",str(listing),
         "-an","-c:v","libx264","-preset","medium","-crf","17","-pix_fmt","yuv420p",str(temp)])
    run(["ffmpeg","-y","-loglevel","error","-i",str(temp),"-vf",
         f"scale={OW}:{OH}:flags=lanczos","-an","-c:v","libx264","-preset","medium",
         "-crf","17","-pix_fmt","yuv420p","-movflags","+faststart",str(output)])
    run(["ffprobe","-v","error","-show_entries",
         "stream=width,height,codec_name:format=duration,size","-of","default=noprint_wrappers=1",str(output)])

TOURETTE = [
 {"src":"t_hands","kind":"comment","title":"É só se controlar.","sub":"Mas ninguém viu o que aconteceu depois.","dur":2.8,"start":0,"bias":-.45},
 {"src":"t_sofa","kind":"editorial","title":"eu tentei segurar.","sub":"por segundos que pareceram minutos","dur":3.0,"start":1,"bias":.4},
 {"src":"t_hands","kind":"editorial","title":"a tensão subiu.","sub":"mãos • pescoço • respiração","dur":3.1,"start":4,"bias":.48},
 {"src":"t_pressure","kind":"counter","title":"Quanto mais cobrança, mais pressão.","sub":"E o corpo não vira obediente porque alguém mandou.","dur":3.2,"start":1,"bias":-.35},
 {"src":"t_sofa","kind":"fact","title":"Tiques são movimentos ou sons involuntários.","sub":"A pessoa não escolhe ter um tique.","dur":3.5,"start":5,"bias":-.3},
 {"src":"t_release","kind":"fact","title":"Algumas pessoas conseguem suprimir por pouco tempo.","sub":"Isso pode gerar desconforto e tensão.","dur":3.4,"start":1,"bias":.5},
 {"src":"t_support","kind":"contrast","title":"“Para com isso.”","sub":"“Quer que eu te dê espaço?”","dur":3.3,"start":0,"bias":.42},
 {"src":"t_support","kind":"editorial","title":"acolher muda a cena.","sub":"menos vigilância • mais segurança","dur":2.9,"start":4,"bias":-.42},
 {"src":"t_hands","kind":"cta","title":"Tique não é falta de educação.","sub":"Compartilhe para trocar julgamento por informação.","dur":3.8,"start":8,"bias":.35},
]

TDL = [
 {"src":"d_phone","dur":2.7,"start":0,"bias":.45,"messages":[("them","Me responde rápido: o que aconteceu?"),("typing","")]},
 {"src":"d_message","dur":3.2,"start":1,"bias":-.42,"messages":[("them","Você entendeu a pergunta?"),("typing","")],"timer":"3 segundos..."},
 {"src":"d_wait","dur":3.4,"start":0,"bias":.35,"messages":[("dim","Ela entendeu."),("dim","Ela sabe a resposta.")],"insight":"A linguagem ainda está sendo organizada.","label":"POR DENTRO"},
 {"src":"d_clock","dur":3.3,"start":1,"bias":-.3,"messages":[("them","Fala logo."),("typing","")],"timer":"o tempo vira pressão"},
 {"src":"d_phone","dur":3.2,"start":5,"bias":-.4,"messages":[("them","Então você não sabe?"),("me","Eu sei... só preciso...")],"insight":"A pressa interrompe a resposta.","label":"A VIRADA"},
 {"src":"d_write","dur":3.6,"start":0,"bias":.48,"messages":[("dim","TDL ≠ falta de inteligência")],"insight":"TDL afeta o desenvolvimento e o uso da linguagem.","label":"O FATO"},
 {"src":"d_message","dur":3.4,"start":6,"bias":.38,"messages":[("them","Vou perguntar uma coisa por vez."),("typing","")],"insight":"Uma pergunta reduz a sobrecarga.","label":"FAÇA ASSIM"},
 {"src":"d_wait","dur":3.5,"start":5,"bias":-.4,"messages":[("them","Pode pensar. Eu espero."),("typing","")],"timer":"pausa de verdade"},
 {"src":"d_write","dur":3.7,"start":5,"bias":-.35,"messages":[("them","Quer escrever ou apontar?")],"steps":["uma pergunta","uma pausa","um apoio visual"]},
 {"src":"d_phone","dur":3.5,"start":10,"bias":.42,"messages":[("me","Agora consigo responder."),("them","Estou ouvindo.")],"insight":"Dar tempo também é comunicação.","label":"RESULTADO"},
 {"src":"d_message","dur":4.2,"start":10,"bias":-.35,"messages":[("dim","Antes de dizer “fala logo”...")],"insight":"Salve e envie este vídeo para quem precisa aprender a esperar.","label":"LEVE ESTA IDEIA"},
]

if __name__ == "__main__":
    assemble("Video_1_Tourette_documental_v3", "doc", TOURETTE)
    assemble("Video_2_TDL_conversa_v3", "chat", TDL)
