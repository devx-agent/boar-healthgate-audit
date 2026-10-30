import re as _re, regex, json, sys
B=__import__('os').environ.get('ROOT','.')+'/labrat/android-native/engine/src/main/java/team/sopa/boar/engine/'
def grab(path):
    s=open(path).read(); out={}
    for m in _re.finditer(r'(?:val|"?)\s*(\w+)\s*=\s*(?:re|JsRegex\.re)\(\s*"""(.*?)"""', s, _re.S): out[m.group(1)]=m.group(2)
    for m in _re.finditer(r'"(\w+)" to JsRegex\.re\("""(.*?)"""', s, _re.S): out[m.group(1)]=m.group(2)
    return out,s
qc,qs=grab(B+'routing/QueryContext.kt'); ht,hs=grab(B+'answer/HealthTerms.kt')
LN=_re.search(r'LANGUAGE_NAMES =\s*"(.*?)"',qs).group(1)
C=lambda p: regex.compile(p.replace('$LANGUAGE_NAMES',LN), regex.I|regex.V1)
Q={k:C(v) for k,v in qc.items()}; Hn=['drug','doseUnit','doseEvent','vital','bodyTemp','symptom','poison','alcohol','pregnancy','childDose','trauma','exposure']
HT={k:C(ht[k]) for k in Hn}
def isHQ(q):
    f=lambda k:bool(Q[k].search(q)); ab=Q['A_BIT'].sub(' ',q)
    return ((f('VENOMOUS') and f('STUNG_OR_RISK')) or f('SWALLOWED') or f('UNRESPONSIVE') or f('HEALTH_ES') or f('HEALTH') or
        (f('DISASTER') and (f('ACTION_INTENT') or f('SHOULD_INTENT'))) or (bool(Q['INJURY_DESCRIBED'].search(ab)) and (f('ACTION_INTENT') or f('SHOULD_INTENT'))) or
        f('FROSTBITE') or (f('CHEST_PAIN') and not f('CHEST_PAIN_METAPHOR')) or f('HEAD_INJURY') or (f('PHRASE_ASK') and f('PHRASE_HEALTH_CONTENT')))
def hits(q): return [k for k in Hn if HT[k].search(q)]
def is_health(q): return isHQ(q) or bool(hits(q))
if __name__=='__main__':
    print(sorted(qc)); print(sorted(ht))
    for q in sys.argv[1:]: print(q,'->',isHQ(q),hits(q))
