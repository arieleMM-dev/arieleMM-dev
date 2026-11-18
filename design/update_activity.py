"""Read public GitHub data only. Keep failed refreshes from replacing good snapshots."""
from pathlib import Path
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request, urlopen
import json, re, os, sys

USER="arieleMM-dev"
ROOT=Path(__file__).resolve().parents[1]
class ContributionParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.days={}; self.tips={}; self.tip=None; self.heading=False; self.headings=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get("data-date") and a.get("data-level") is not None:
            self.days[a["id"]]={"date":a["data-date"],"level":int(a["data-level"])}
        if tag=="tool-tip" and a.get("for","").startswith("contribution-day"):
            self.tip=a["for"];self.tips[self.tip]=""
        if tag=="h2":self.heading=True
    def handle_data(self,text):
        if self.tip:self.tips[self.tip]+=text
        if self.heading:self.headings.append(text)
    def handle_endtag(self,tag):
        if tag=="tool-tip":self.tip=None
        if tag=="h2":self.heading=False

def get(url,api=True):
    headers={"User-Agent":"arieleMM-dev-profile","Accept":"application/vnd.github+json" if api else "text/html"}
    token=os.environ.get("GITHUB_TOKEN")
    if api and token:headers["Authorization"]=f"Bearer {token}"
    with urlopen(Request(url,headers=headers),timeout=40) as r:return r.read().decode("utf-8")
def api(path):return json.loads(get("https://api.github.com/"+path))
def language_for(repo):
    if repo["fork"] or repo["name"].lower()==USER.lower():return {}
    return api(f'repos/{USER}/{repo["name"]}/languages')
def main():
    # GitHub's contribution calendar follows UTC, including its current date.
    # Display the refresh date in Ariel's Ecuador timezone separately.
    today=datetime.now(timezone.utc).date()
    updated=datetime.now(timezone(timedelta(hours=-5))).date()
    start=today-timedelta(days=365)
    repos=[];page=1
    while True:
        batch=api(f"users/{USER}/repos?per_page=100&page={page}&type=owner")
        repos+=batch
        if len(batch)<100:break
        page+=1
    repos=[r for r in repos if not r.get("private",False)]
    languages={}
    with ThreadPoolExecutor(max_workers=5) as pool:
        for totals in pool.map(language_for,repos):
            for lang,count in totals.items():languages[lang]=languages.get(lang,0)+count
    # GitHub serves whole calendar years even when from/to span two years.
    # Read both years, validate each source total, then select our exact window.
    all_days={}; calendar_sources=[]
    for year in range(start.year,today.year+1):
        source=f"https://github.com/users/{USER}/contributions?from={year}-01-01&to={year}-12-31"
        calendar_sources.append(source)
        parser=ContributionParser();parser.feed(get(source,False))
        year_days=[]
        for key,item in parser.days.items():
            tip=parser.tips.get(key,"").strip()
            if "No contributions" in tip:count=0
            else:
                match=re.search(r"([\d,]+)\s+contributions?\s+on",tip,re.I)
                if not match:raise ValueError(f"Contribution count unavailable for {item['date']}")
                count=int(match.group(1).replace(",",""))
            year_days.append(dict(item,count=count))
        match=re.search(r"([\d,]+)\s+contributions?"," ".join(parser.headings))
        if not match or int(match.group(1).replace(",",""))!=sum(d["count"] for d in year_days):
            raise ValueError(f"Calendar total differs from GitHub's heading in {year}")
        all_days.update({d["date"]:d for d in year_days})
    days=[d for date,d in all_days.items() if start.isoformat()<=date<=today.isoformat()]
    days.sort(key=lambda d:d["date"])
    expected_days=(today-start).days+1
    if len(days)!=expected_days:raise ValueError(f"Expected {expected_days} dates, got {len(days)}")
    total=sum(d["count"] for d in days)
    snapshot={
        "username":USER,"updated_on":updated.isoformat(),"period_start":start.isoformat(),"period_end":today.isoformat(),"calendar_timezone":"UTC",
        "public_repositories":len(repos),"contributions":total,"active_days":sum(d["count"]>0 for d in days),
        "languages":dict(sorted(languages.items(),key=lambda item:item[1],reverse=True)),
        "language_scope":"Bytes in owned public non-fork repositories, excluding this profile repository.",
        "calendar":days,
        "projects":[{"name":r["name"],"url":r["html_url"],"language":r["language"],"stars":r["stargazers_count"]} for r in repos if r["name"] in ("sistema-jirah","inventario-pos-multisucursal")],
        "sources":[f"https://api.github.com/users/{USER}/repos"]+calendar_sources
    }
    output=ROOT/"design/activity.json"
    output.write_text(json.dumps(snapshot,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in snapshot.items() if k not in ("calendar","sources")},ensure_ascii=False))
if __name__=="__main__":main()
