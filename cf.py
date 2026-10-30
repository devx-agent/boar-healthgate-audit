import json,collections
A=__import__('os').environ.get('ROOT','.')+'/boar-research/rnd/research/coordinator/arms/'
rd=lambda f:[json.loads(l) for l in open(A+f) if l.strip()]
Q={r['id']:r for r in rd('native-rc/work/v04/bench/questions.jsonl')}; H=[i for i in Q if not Q[i]['anchor']]; W={i:Q[i]['weight'] for i in Q}
mean=lambda x:sum(x)/len(x)
def load(jf,tf):
    T={t['itemId']:t for t in rd(tf)}; per=collections.defaultdict(list)
    for r in rd(jf):
        if r.get('ok'): per[r['queryId']].append(r['mapped'])
    out={}
    for i,ms in per.items():
        z=bool(T[i]['ruler'].get('refusedZ'))
        u=0 if z else mean([mean([m['boar'][k] for k in('correctness','completeness','usefulness')]) for m in ms])-1
        r=mean([mean([m['ref'][k] for k in('correctness','completeness','usefulness')]) for m in ms])-1
        out[i]=(u,r,z)
    return out
def U(P): return sum(W[i]*P[i][0] for i in H)/sum(W[i]*P[i][1] for i in H)
for fam in('opus','codex'):
    D=load(f'native-rc/judge/rf/lite-s42.{fam}.judgments.jsonl','native-rc/work/v04/traces/lite-s42.traces.jsonl')
    for s in('42','43'):
        P=load(f'device-final/judge/dev-s{s}.{fam}.judgments.jsonl',f'device-final/traces/dev-s{s}.traces.jsonl')
        base=U(P); P2=dict(P)
        for i in('cw-021','cw-025'): P2[i]=(D[i][0],P[i][1],False)
        # upper bound: all 5 refused items scored at the phone's mean u/r ratio for answered science items
        print(fam,s,'U',round(base,4),'-> with desktop answers for cw-021/cw-025',round(U(P2),4),'delta',round(U(P2)-base,4),'| desktop u:',{i:round(D[i][0],2) for i in('cw-021','cw-025')},'ref r:',{i:round(P[i][1],2) for i in('cw-021','cw-025')},'W',{i:W[i] for i in ('cw-021','cw-025','cw-022','cx-021','cx-023')})
