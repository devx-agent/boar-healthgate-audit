"""Reproduce the HealthGate provenance-licensing findings.
ROOT must contain: boar-research/ (github.com/r4topunk/boar-research), boar-bench/, labrat/ (labrat-boar-fork),
with boar-traces (huggingface.co/datasets/r4topunk/boar-traces) copied into the same paths inside boar-research/.
Usage: ROOT=/path python3 reproduce.py"""
import json, glob, os, collections
R=os.environ.get('ROOT','.')
exec(open(os.path.join(os.path.dirname(__file__),'gate.py')).read().split("if __name__")[0])
exec(open(os.path.join(os.path.dirname(__file__),'newrule.py')).read())
A=R+'/boar-research/rnd/research/coordinator/arms/'
HP={"boar-firstaid-en","boar-medlineplus-en","qa-health-se"}
rd=lambda f:[json.loads(l) for l in open(A+f) if l.strip()]
qs={q['id']:q for q in rd('native-rc/work/v04/bench/questions.jsonl')}
print('== 1. Desktop twin (lite-s42): health-classified turns and the health-pack chunk that licensed them')
for r in rd('native-rc/work/v04/lite-s42.jsonl'):
    first=qs[r['id']]['question'].split('\n')[0].replace('[Turn 1] ','')
    for t in r['turns']:
        if is_health(first) or t['path']!='model':
            hk=[(k['chunkId'].split(':')[1],k.get('matchType'),round(k.get('score',0),2),k['title'][:40]) for k in t.get('kept',[]) if k['chunkId'].split(':')[1] in HP]
            print(' ',r['id'],'turn',t['turn'],'path',t['path'],'| sources',t.get('sourcesShownTitles'),'| health-pack kept',hk)
print('== 2. Phone (DEVICE-FINAL M1) healthFixed per item, seeds 42/43')
for s in ('42','43'):
    P=[x for x in rd(f'device-final/traces/dev-s{s}.traces.jsonl')]
    print('  s'+s,'refused (ruler.refusedZ):',sorted(x['itemId'] for x in P if x['ruler'].get('refusedZ')))
print('== 3. Phone non-health rows that kept MedlinePlus passages (provenance != relevance)')
for r in rd('device-final/out/df-m1-v04-s42.jsonl'):
    m=[x for x in r.get('retrievedTitles',[]) if x.startswith('MedlinePlus')]
    if m and not is_health(r['query']): print(' ',r['queryId'],m,'|',r['query'][:60])
print('== 4. M2 probes (phone s42): gate classification vs path')
c=collections.Counter(); miss=[]
for r in rd('device-final/out/df-m2-probes-s42.jsonl'):
    h=is_health(r['query']); c[(h,r['healthFixed'])]+=1
    if not h and not r['healthFixed']: miss.append((r['queryId'],r['query'][:60]))
print(' ',dict(c)); [print('   lexical miss ->',m) for m in miss]
print('== 5. Proposed rule: fires on probes', [r['queryId'] for r in rd('device-final/out/df-m2-probes-s42.jsonl') if NEW.search(r['query'])])
tot=0; extra=[]
for f in sorted(glob.glob(R+'/boar-bench/bench/**/*.json*',recursive=True)):
    if 'refs' in f: continue
    try: q=[json.loads(l) for l in open(f) if l.strip()]
    except Exception:
        try: q=json.load(open(f)); q=q if isinstance(q,list) else q.get('items',q.get('questions',[]))
        except Exception: continue
    q=[x for x in q if isinstance(x,dict) and isinstance(x.get('question'),str)]; tot+=len(q)
    extra+=[x['question'][:80] for x in q if NEW.search(x['question']) and not is_health(x['question'])]
print(f'  boar-bench questions scanned {tot}, new-rule-only fires {len(extra)}', extra[:5])
