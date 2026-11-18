"""Validate the public data window and self-contained GitHub image assets."""
from pathlib import Path
from datetime import date,timedelta
import json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def main():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    refs=re.findall(r'(?:src|srcset)="([^"]+)"',readme)
    assert refs and all((ROOT/ref).is_file() for ref in refs),"A README image is missing"
    assert "profile/test" not in readme and "sale.concurrency.test" not in readme
    for ref in set(refs):
        tree=ET.parse(ROOT/ref)
        assert tree.getroot().tag.endswith("svg")
        for node in tree.iter():
            assert node.tag.split("}")[-1] not in ("script","foreignObject","image")
            assert not any(k.split("}")[-1] in ("href","onload","onclick") for k in node.attrib)
    data=json.loads((ROOT/"design/activity.json").read_text())
    days=data["calendar"]
    begin=date.fromisoformat(data["period_start"]);end=date.fromisoformat(data["period_end"])
    assert len(days)==(end-begin).days+1
    assert [x["date"] for x in days]==[(begin+timedelta(days=i)).isoformat() for i in range(len(days))]
    assert all(isinstance(x["count"],int) and x["count"]>=0 for x in days)
    assert sum(x["count"] for x in days)==data["contributions"]
    assert sum(x["count"]>0 for x in days)==data["active_days"]
    assert data["public_repositories"]>=len(data["projects"])>0
    assert sum(data["languages"].values())>0
    layout=json.loads((ROOT/"design/text-layout.json").read_text())
    stack_lines=[x["text"] for x in layout if x["asset"].startswith("Backend stack:")]
    assert "PostgreSQL" in stack_lines and not any("SQLite" in x for x in stack_lines)
    assert any(x["text"]=="Connect with me" for x in layout)
    assert not any("Connect with Ariel" in x["text"] for x in layout)
    for name in ("hero.svg","hero-mobile.svg","activity.svg","activity-mobile.svg"):
        svg=(ROOT/"assets/profile"/name).read_text()
        assert "@keyframes" in svg and "prefers-reduced-motion" in svg
    print(f"Validated {len(refs)} image references, {len(days)} source dates, calendar totals and requested profile corrections.")
if __name__=="__main__":main()
