from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from LinkSnip.models import Link
from database import init_db, read_db, write_db
from datetime import datetime

app = FastAPI()
app.mount("/", StaticFiles(directory="static", html=True), name="static")


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/shorten")
async def shorten_link(link: Link):
    db = read_db()
    slug = link.slug or str(hash(link.url))[:6]
    if slug in db:
        raise HTTPException(status_code=400, detail="Slug already taken")
    db[slug] = {"url": link.url, "clicks": 0, "last_click": None}
    write_db(db)
    return {"short_url": f"/{slug}"}

@app.get("/{slug}")
async def redirect_link(slug: str):
    db = read_db()
    if slug not in db:
        raise HTTPException(status_code=404, detail="Link not found")
    db[slug]["clicks"] += 1
    db[slug]["last_click"] = datetime.utcnow().isoformat()
    write_db(db)
    return {"redirect": db[slug]["url"]}

@app.get("/stats/{slug}")
async def get_stats(slug: str):
    db = read_db()
    if slug not in db:
        raise HTTPException(status_code=404, detail="Link not found")
    return {
        "slug": slug,
        "original_url": db[slug]["url"],
        "clicks": db[slug]["clicks"],
        "last_click": db[slug]["last_click"]
    }
