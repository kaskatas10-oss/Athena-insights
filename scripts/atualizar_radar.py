#!/usr/bin/env python3
"""Coleta manchetes RSS com fonte e data; não gera análises inventadas."""
import json, pathlib, urllib.request, urllib.parse, xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
TOPICS={
"ia":[("Inteligência artificial","inteligência artificial tecnologia"),("Modelos e agentes","ChatGPT OpenAI Claude Gemini modelos IA"),("Segurança de IA","segurança inteligência artificial riscos")],
"executivo":[("IA em operações","IA logística automação operações"),("ESG","ESG sustentabilidade empresas"),("Qualidade e processos","qualidade processos melhoria contínua"),("Transportes e seguros","seguro de transporte logística riscos"),("Lean Six Sigma","Lean Six Sigma melhoria contínua")]}
def collect(query,limit=3):
    url="https://news.google.com/rss/search?"+urllib.parse.urlencode({"q":query+" when:4d","hl":"pt-BR","gl":"BR","ceid":"BR:pt-419"})
    req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 AthenaInsights/1.0"})
    with urllib.request.urlopen(req,timeout=35) as response:
        data=response.read(1_500_000)
    root=ET.fromstring(data)
    out=[]
    for node in root.findall("./channel/item")[:limit]:
        title=node.findtext("title","").strip()
        href=node.findtext("link","").strip()
        source=node.find("source")
        date=node.findtext("pubDate","")
        if title and href.startswith("https://"):
            out.append({"title":title[:260],"url":href,"source":(source.text or "").strip() if source is not None else "Google Notícias","published":date})
    return out
result={"updated_at":datetime.now(timezone.utc).isoformat(),"method":"Clipping automático de manchetes via Google Notícias RSS; não substitui a curadoria analítica dos briefings."}
for category,topics in TOPICS.items():
    result[category]=[]
    for name,query in topics:
        try: records=collect(query)
        except Exception as exc:
            print("Falha na coleta de",name,":",str(exc)[:140])
            records=[]
        result[category].append({"topic":name,"items":records})
if not any(t["items"] for cat in TOPICS for t in result[cat]):
    raise RuntimeError("Nenhuma fonte retornou manchetes; preservando última edição")
pathlib.Path("data").mkdir(exist_ok=True)
pathlib.Path("data/radar.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
