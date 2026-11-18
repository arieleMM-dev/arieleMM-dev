"""Build the GitHub profile's self-contained SVG artwork. Python + fontTools."""
from pathlib import Path
from html import escape
import json, xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/"assets"/"profile"
ASSETS.mkdir(parents=True,exist_ok=True)
BG="#17191c"; SURFACE="#1e2125"; EDGE="#383d43"
FG="#f0f1ee"; SECOND="#b7bdc5"; ACCENT="#c4d2c8"
fonts={}
for weight in (400,500,600,700):
    f=instantiateVariableFont(TTFont(ROOT/"design/fonts/Manrope.ttf"),{"wght":weight},inplace=True)
    fonts[weight]=(f.getGlyphSet(),f.getBestCmap(),f["head"].unitsPerEm)
bounds=[]

class Canvas:
    def __init__(self,w,h,title):
        self.w=w; self.h=h; self.title=title
        self.parts=[f'<rect width="{w}" height="{h}" rx="20" fill="{BG}"/>']
    def add(self,s): self.parts.append(s)
    def text(self,txt,x,y,size=28,color=FG,weight=400,anchor="start",spacing=0):
        # GitHub adds horizontal padding on phones; keep copy readable at ~280 px.
        if self.w == 640:
            size=max(size,32)
        gs,cm,up=fonts[weight]; scale=size/up
        widths=[gs[cm[ord(c)]].width*scale for c in txt]
        total=sum(widths)+spacing*max(0,len(txt)-1)
        if anchor=="middle": x-=total/2
        if anchor=="end": x-=total
        start=x; pen=SVGPathPen(gs, ntos=lambda n: format(round(n,2),'.2f').rstrip('0').rstrip('.') if round(n,2) else '0')
        for c,advance in zip(txt,widths):
            gs[cm[ord(c)]].draw(TransformPen(pen,(scale,0,0,-scale,x,y)))
            x+=advance+spacing
        if start<0 or x>self.w+0.1 or y>self.h:
            raise ValueError(f"Text overflow {self.title}: {txt}, {start}..{x}, y={y}")
        bounds.append(dict(asset=self.title,text=txt,x=round(start,1),end=round(x,1),y=y,size=size))
        self.add(f'<path fill="{color}" d="{pen.getCommands()}"/>')
    def line(self,x1,y1,x2,y2,color=EDGE,width=1.4):
        self.add(f'<path d="M{x1} {y1}H{x2}" stroke="{color}" stroke-width="{width}"/>' if y1==y2 else f'<path d="M{x1} {y1}L{x2} {y2}" stroke="{color}" stroke-width="{width}"/>')
    def rect(self,x,y,w,h,fill=SURFACE,r=12,stroke=None):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}"' if stroke else '')+'/>')
    def logo(self,name,x,y,size=48,color=FG):
        svg=ET.parse(ROOT/f"design/icons/{name}.svg").getroot()
        paths="".join(f'<path d="{p.attrib["d"]}"/>' for p in svg.iter() if p.tag.endswith("path"))
        self.add(f'<g transform="translate({x} {y}) scale({size/24})" fill="{color}">{paths}</g>')
    def icon(self,kind,x,y,size=32,color=FG):
        # Tabler Icons, MIT. https://github.com/tabler/tabler-icons
        paths={
            "arrow":'<path d="M7 17l10 -10M7 7h10v10"/>',
            "flow":'<path d="M6 3v12a3 3 0 0 0 3 3h6M18 6a6 6 0 0 1 -6 6H6"/><circle cx="6" cy="3" r="2"/><circle cx="18" cy="3" r="2"/><circle cx="18" cy="18" r="2"/>',
            "check":'<path d="M5 12l4 4l10 -10"/>',
            "linkedin":'<path d="M4 4m0 2a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2zM8 11v5M8 8v.01M12 16v-5M16 16v-3a2 2 0 0 0 -4 0"/>',
            "world":'<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15.3 15.3 0 0 1 0 18a15.3 15.3 0 0 1 0 -18"/>',
        }
        self.add(f'<g transform="translate({x} {y}) scale({size/24})" fill="none" stroke="{color}" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{paths[kind]}</g>')
    def save(self,name):
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img" aria-labelledby="title"><title id="title">{escape(self.title)}</title>'+''.join(self.parts)+'</svg>\n'
        (ASSETS/name).write_text(svg,encoding="utf-8")

def plate(c,x,y,w,label):
    # A semantic layer diagram: request -> application -> persistence.
    d=f"M{x} {y}l{w/2} -45l{w/2} 45l-{w/2} 45z"
    c.add(f'<path d="{d}" fill="{SURFACE}" stroke="#69766f" stroke-width="1.4"/>')
    c.add(f'<path d="M{x} {y}v12l{w/2} 45l{w/2} -45v-12" fill="none" stroke="{EDGE}" stroke-width="1.4"/>')
    c.text(label,x+w/2,y+10,24,SECOND,500,"middle")

def hero(mobile=False):
    c=Canvas(640 if mobile else 1200,810 if mobile else 530,"Ariel Morillo. Software developer focused on backend.")
    if not mobile:
        c.text("Ariel Morillo",56,76,34,FG,600)
        c.text("Backend",51,221,102,FG,600,spacing=-2.4)
        c.text("developer.",51,331,102,ACCENT,600,spacing=-2.4)
        c.text("Building APIs and data-driven applications",56,410,28,SECOND)
        c.text("with Node.js and TypeScript.",56,450,28,SECOND)
        c.line(794,96,794,448)
        c.line(980,185,980,403,"#75857c",2)
        plate(c,844,182,272,"HTTP")
        plate(c,844,270,272,"Node.js")
        plate(c,844,358,272,"SQL")
        c.text("Software Engineering student",56,501,24,SECOND)
    else:
        c.text("Ariel Morillo",36,66,32,FG,600)
        c.text("Backend",32,168,79,FG,600,spacing=-1.7)
        c.text("developer.",32,254,79,ACCENT,600,spacing=-1.7)
        c.text("Building APIs and data-driven",36,322,28,SECOND)
        c.text("applications with Node.js",36,362,28,SECOND)
        c.text("and TypeScript.",36,402,28,SECOND)
        c.line(320,480,320,688,"#75857c",2)
        plate(c,164,506,312,"HTTP")
        plate(c,164,586,312,"Node.js")
        plate(c,164,666,312,"SQL")
        c.text("Software Engineering student",36,776,25,SECOND)
    c.save("hero-mobile.svg" if mobile else "hero.svg")

def stack(mobile=False):
    c=Canvas(640 if mobile else 1200,760 if mobile else 422,"Backend stack: Node.js, TypeScript, Express, Prisma, Docker, Vitest and CI/CD. Data: PostgreSQL and SQLite.")
    c.text("Backend stack",36 if mobile else 56,72,37 if mobile else 42,FG,600)
    names=[("node","Node.js"),("ts","TypeScript"),("express","Express"),("prisma","Prisma"),("docker","Docker"),("vitest","Vitest"),("flow","CI/CD")]
    if mobile:
        for i,(icon,label) in enumerate(names):
            if i<6:
                x=150 if i%2==0 else 470; y=142+(i//2)*165
                c.logo(icon,x-27,y,54)
                c.text(label,x,y+100,29,SECOND,500,"middle")
            else:
                c.line(36,636,604,636)
                c.icon("flow",43,674,46,ACCENT)
                c.text("CI/CD",115,710,30,FG,500)
                c.text("PostgreSQL / SQLite",604,710,26,SECOND,400,"end")
    else:
        for i,(icon,label) in enumerate(names):
            x=(176+i*282) if i<4 else (270+(i-4)*330)
            y=120 if i<4 else 266
            if icon=="flow": c.icon(icon,x-24,y,48,ACCENT)
            else:c.logo(icon,x-24,y,48)
            c.text(label,x,y+94,29,SECOND,500,"middle")
        c.line(56,240,1144,240)
        c.text("PostgreSQL / SQLite",1144,400,22,SECOND,400,"end")
    c.save("stack-mobile.svg" if mobile else "stack.svg")

def worktitle():
    for mobile in (False,True):
        c=Canvas(640 if mobile else 1200,126 if mobile else 132,"Selected work. Backend projects.")
        c.text("Selected work",36 if mobile else 56,80,37 if mobile else 42,FG,600)
        c.save("work-mobile.svg" if mobile else "work.svg")

def database(c,x,y,w=160):
    c.add(f'<g fill="{SURFACE}" stroke="#67766d" stroke-width="1.5"><path d="M{x} {y+20}v76c0 28 {w} 28 {w} 0v-76"/><ellipse cx="{x+w/2}" cy="{y+20}" rx="{w/2}" ry="23"/><path d="M{x} {y+55}c0 28 {w} 28 {w} 0M{x} {y+90}c0 28 {w} 28 {w} 0"/></g>')

def inventory(mobile=False):
    c=Canvas(640 if mobile else 1200,790 if mobile else 455,"Inventory and POS. Multi-branch inventory, PostgreSQL persistence, and concurrent sales integration tests. Node.js, TypeScript, Express and Prisma. Explore repository.")
    x=36 if mobile else 56
    c.text("Inventory & POS",x,86,40 if mobile else 49,FG,600)
    if mobile:
        for i,line in enumerate(["Multi-branch inventory and sales.","PostgreSQL persistence and","integration tests for concurrent sales."]):
            c.text(line,x,149+i*40,27,SECOND)
        c.text("Node.js / TypeScript / Express",x,317,26,ACCENT,500)
        c.text("Prisma / PostgreSQL / Vitest",x,355,26,ACCENT,500)
        # Branches -> application -> PostgreSQL. Schema diagram, not live status.
        c.rect(36,435,180,70,stroke=EDGE);c.text("Branches",126,480,25,SECOND,500,"middle")
        c.line(216,470,278,470,"#75857c",2)
        c.rect(278,435,170,70,stroke="#75857c");c.text("Sales API",363,480,25,FG,500,"middle")
        c.line(363,505,363,555,"#75857c",2)
        database(c,283,565)
        c.text("PostgreSQL",363,729,26,SECOND,400,"middle")
        c.text("Explore repository",36,771,27,FG,600)
        c.icon("arrow",575,743,34)
    else:
        c.text("Multi-branch inventory and sales.",x,157,28,SECOND)
        c.text("PostgreSQL persistence and integration",x,199,28,SECOND)
        c.text("tests for concurrent sales.",x,241,28,SECOND)
        c.text("Node.js / TypeScript / Express",x,315,25,ACCENT,500)
        c.text("Prisma / PostgreSQL / Vitest",x,353,25,ACCENT,500)
        c.text("Explore repository",x,413,27,FG,600);c.icon("arrow",326,385,35)
        c.line(760,90,760,366)
        for y,label in [(122,"Branches"),(222,"Sales API")]:
            c.rect(829,y,260,64,stroke=EDGE if y==122 else "#75857c")
            c.text(label,959,y+43,25,SECOND if y==122 else FG,500,"middle")
        c.line(959,186,959,222,"#75857c",2)
        c.line(959,286,959,315,"#75857c",2)
        database(c,879,310)
    c.save("inventory-mobile.svg" if mobile else "inventory.svg")

def jirah(mobile=False):
    c=Canvas(640 if mobile else 1200,675 if mobile else 380,"Finca Jirah. Agricultural traceability and offline field capture. TypeScript, Next.js, Prisma and SQLite/libSQL. Explore repository.")
    x=36 if mobile else 56
    c.text("Finca Jirah",x,86,40 if mobile else 49,FG,600)
    if mobile:
        c.text("Agricultural traceability with",x,151,28,SECOND)
        c.text("offline field capture.",x,193,28,SECOND)
        c.text("TypeScript / Next.js",x,266,26,ACCENT,500)
        c.text("Prisma / SQLite / libSQL",x,304,26,ACCENT,500)
        c.rect(36,378,568,186,fill="#20272a")
        c.text("Field data",66,429,27,SECOND,500)
        c.line(66,460,572,460,"#54635c")
        c.text("Prisma",66,520,32,FG,600)
        c.text("SQLite",444,520,32,FG,500)
        c.line(201,509,404,509,"#7c8e81",2)
        c.text("Explore repository",36,640,27,FG,600);c.icon("arrow",575,611,34)
    else:
        c.text("Agricultural traceability with",x,153,28,SECOND)
        c.text("offline field capture.",x,195,28,SECOND)
        c.text("TypeScript / Next.js / Prisma",x,263,25,ACCENT,500)
        c.text("SQLite / libSQL",x,301,25,ACCENT,500)
        c.text("Explore repository",x,351,27,FG,600);c.icon("arrow",326,323,35)
        c.rect(796,70,348,270,fill="#20272a")
        c.text("Field data",824,119,26,SECOND,500)
        c.line(824,149,1116,149,"#54635c")
        c.logo("prisma",824,187,48,ACCENT); c.text("Prisma",902,225,32,FG,600)
        c.line(847,249,847,283,"#7c8e81",2)
        c.text("SQLite / libSQL",879,302,25,SECOND)
    c.save("jirah-mobile.svg" if mobile else "jirah.svg")

def evidence(mobile=False):
    c=Canvas(640 if mobile else 1200,172 if mobile else 110,"Read the Vitest integration test for concurrent sales.")
    c.logo("vitest",36 if mobile else 52,52 if mobile else 32,48,ACCENT)
    if mobile:
        c.text("Concurrent sales",110,75,29,FG,600)
        c.text("Read the integration test",110,122,25,SECOND)
        c.icon("arrow",575,66,34)
    else:
        c.text("Concurrent sales",126,67,29,FG,600)
        c.text("Read the integration test",1108,67,25,SECOND,400,"end")
        c.icon("arrow",1132,37,34)
    c.save("test-mobile.svg" if mobile else "test.svg")

def contacts():
    for kind,label,url,sub in [
        ("linkedin","LinkedIn","https://www.linkedin.com/in/ariel-morillo-dev","Connect with Ariel"),
        ("world","Portfolio","https://arielmorillo-dev.vercel.app/","Explore my work")]:
        for mobile in (False,True):
            c=Canvas(640 if mobile else 1200,160 if mobile else 118,f"{label}. {sub}. {url}")
            c.icon(kind,38 if mobile else 55,49 if mobile else 35,48 if mobile else 44,ACCENT)
            c.text(label,113 if mobile else 128,85 if mobile else 76,34,FG,600)
            if not mobile:c.text(sub,1104,75,27,SECOND,400,"end")
            c.icon("arrow",574 if mobile else 1132,58 if mobile else 41,34)
            c.save(f"contact-{kind}{'-mobile' if mobile else ''}.svg")

for fn in (hero,stack,inventory,jirah,evidence):
    fn(False);fn(True)
worktitle(); contacts()
(ROOT/"design"/"text-layout.json").write_text(json.dumps(bounds,indent=2),encoding="utf-8")
print(f"Built {len(list(ASSETS.glob('*.svg')))} graphics; {len(bounds)} text lines checked for horizontal overflow.")
