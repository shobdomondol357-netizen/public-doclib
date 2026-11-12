import json
from fastapi import APIRouter, Request, Response
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Document, Category
from .search import keyword_search, tfidf_search

router = APIRouter()

def db():
    return SessionLocal()

TOOLS = [
    {"name":"search_documents","description":"Search documents by keyword in title, tags, description and content.","inputSchema":{"type":"object","properties":{"query":{"type":"string"},"limit":{"type":"integer","default":10}},"required":["query"]}},
    {"name":"get_document_metadata","description":"Get metadata for a document by id.","inputSchema":{"type":"object","properties":{"id":{"type":"integer"}},"required":["id"]}},
    {"name":"read_document","description":"Read extracted text content of a document.","inputSchema":{"type":"object","properties":{"id":{"type":"integer"},"max_chars":{"type":"integer","default":8000}},"required":["id"]}},
    {"name":"search_document_content","description":"Search inside document contents and return matching snippets.","inputSchema":{"type":"object","properties":{"query":{"type":"string"},"limit":{"type":"integer","default":10}},"required":["query"]}},
    {"name":"list_categories","description":"List all document categories.","inputSchema":{"type":"object","properties":{}}},
    {"name":"get_document_sections","description":"Get a document split into sections/chunks for easier reading.","inputSchema":{"type":"object","properties":{"id":{"type":"integer"},"chunk_size":{"type":"integer","default":2000}},"required":["id"]}},
]

def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")
    params = msg.get("params") or {}
    if method == "initialize":
        return {"jsonrpc":"2.0","id":mid,"result":{
            "protocolVersion":"2024-11-05",
            "capabilities":{"tools":{}},
            "serverInfo":{"name":"public-doclib","version":"1.0.0"}
        }}
    if method == "notifications/initialized":
        return None
    if method == "tools/list":
        return {"jsonrpc":"2.0","id":mid,"result":{"tools":TOOLS}}
    if method == "tools/call":
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            result = call_tool(name, args)
            return {"jsonrpc":"2.0","id":mid,"result":{"content":[{"type":"text","text":json.dumps(result, ensure_ascii=False)}]}}
        except Exception as e:
            return {"jsonrpc":"2.0","id":mid,"error":{"code":-32000,"message":str(e)}}
    if method == "ping":
        return {"jsonrpc":"2.0","id":mid,"result":{}}
    return {"jsonrpc":"2.0","id":mid,"error":{"code":-32601,"message":"Method not found"}}

def call_tool(name, args):
    s = db()
    try:
        if name == "search_documents":
            q = args.get("query","")
            limit = int(args.get("limit",10))
            docs = keyword_search(s, q, limit)
            return [{"id":d.id,"title":d.title,"category":d.category.name if d.category else None,"text_status":d.text_status,"snippet":(d.text_content or "")[:300]} for d in docs]
        if name == "get_document_metadata":
            d = s.query(Document).filter(Document.id==args["id"], Document.is_deleted==False).first()
            if not d: raise ValueError("not found")
            return {"id":d.id,"title":d.title,"filename":d.filename,"mime_type":d.mime_type,"size_bytes":d.size_bytes,"category":d.category.name if d.category else None,"tags":d.tags,"author":d.author,"subject":d.subject,"text_status":d.text_status,"updated_at":str(d.updated_at)}
        if name == "read_document":
            d = s.query(Document).filter(Document.id==args["id"], Document.is_deleted==False).first()
            if not d: raise ValueError("not found")
            mc = int(args.get("max_chars",8000))
            txt = d.text_content or ""
            return {"id":d.id,"title":d.title,"text": txt[:mc], "truncated": len(txt)>mc}
        if name == "search_document_content":
            q = args.get("query","").lower()
            limit = int(args.get("limit",10))
            docs = s.query(Document).filter(Document.is_public==True, Document.is_deleted==False).all()
            out = []
            for d in docs:
                t = (d.text_content or "").lower()
                if q in t:
                    idx = t.find(q)
                    start = max(0, idx-200)
                    snippet = (d.text_content or "")[start:start+400]
                    out.append({"id":d.id,"title":d.title,"snippet":snippet})
                    if len(out)>=limit: break
            return out
        if name == "list_categories":
            cats = s.query(Category).all()
            return [{"id":c.id,"name":c.name,"slug":c.slug} for c in cats]
        if name == "get_document_sections":
            d = s.query(Document).filter(Document.id==args["id"], Document.is_deleted==False).first()
            if not d: raise ValueError("not found")
            txt = d.text_content or ""
            size = int(args.get("chunk_size",2000))
            chunks = [txt[i:i+size] for i in range(0,len(txt),size)]
            return {"id":d.id,"title":d.title,"sections":[{"index":i,"text":c} for i,c in enumerate(chunks)]}
        raise ValueError("unknown tool")
    finally:
        s.close()

@router.post("/mcp")
async def mcp_post(request: Request):
    body = await request.json()
    # support batch
    if isinstance(body, list):
        resps = []
        for m in body:
            r = handle(m)
            if r is not None:
                resps.append(r)
        return Response(content=json.dumps(resps), media_type="application/json")
    r = handle(body)
    if r is None:
        return Response(status_code=204)
    return r

@router.get("/mcp")
async def mcp_get():
    return {"name":"public-doclib","transport":"streamable-http","endpoint":"/mcp"}
