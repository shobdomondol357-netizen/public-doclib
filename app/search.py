import math, re
from sqlalchemy.orm import Session
from .models import Document

def tokenize(s: str):
    return re.findall(r"\w+", (s or "").lower())

def keyword_search(db: Session, q: str, limit=50):
    ql = q.lower().strip()
    if not ql:
        return []
    terms = tokenize(q)
    docs = db.query(Document).filter(Document.is_public == True, Document.is_deleted == False).all()
    scored = []
    for d in docs:
        hay = " ".join([d.title or "", d.filename or "", d.description or "", d.tags or "", d.author or "", d.subject or "", (d.text_content or "")[:50000]]).lower()
        score = 0
        for t in terms:
            score += hay.count(t)
        if ql in (d.title or "").lower():
            score += 5
        if score > 0:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in scored[:limit]]

def tfidf_search(db: Session, q: str, limit=20):
    # lightweight TF-IDF cosine over documents
    docs = db.query(Document).filter(Document.is_public == True, Document.is_deleted == False).all()
    if not docs:
        return []
    # build corpus
    corpus = []
    for d in docs:
        text = " ".join([d.title or "", d.description or "", d.tags or "", (d.text_content or "")[:20000]])
        corpus.append(tokenize(text))
    qtok = tokenize(q)
    if not qtok:
        return []
    # document frequency
    N = len(corpus)
    df = {}
    for toks in corpus:
        for t in set(toks):
            df[t] = df.get(t, 0) + 1
    idf = {t: math.log((N+1)/(df.get(t,0)+1)) + 1 for t in set(qtok)}

    def vec(tokens):
        tf = {}
        for t in tokens:
            tf[t] = tf.get(t,0)+1
        # normalize tf
        L = len(tokens) or 1
        v = {}
        for t,c in tf.items():
            v[t] = (c/L) * idf.get(t, 1.0)
        return v

    qv = vec(qtok)
    # cosine
    qnorm = math.sqrt(sum(x*x for x in qv.values())) or 1
    results = []
    for idx, toks in enumerate(corpus):
        dv = vec(toks)
        dn = math.sqrt(sum(x*x for x in dv.values())) or 1
        dot = sum(qv.get(t,0)*dv.get(t,0) for t in qv)
        sim = dot/(qnorm*dn)
        if sim > 0:
            results.append((sim, docs[idx]))
    results.sort(key=lambda x: x[0], reverse=True)
    return [d for _, d in results[:limit]]

def semantic_search(db, q, limit=20):
    # try tfidf; could be extended with embeddings
    return tfidf_search(db, q, limit)
