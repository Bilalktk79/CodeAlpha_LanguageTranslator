from fastapi import FastAPI, Form, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests

app = FastAPI(title="AI Smart Translator Pro")

templates = Jinja2Templates(directory="templates")

# ✅ static files serve
app.mount("/static", StaticFiles(directory="static"), name="static")

# ✅ HOME
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ✅ TRANSLATE FUNCTION WITH MULTIPLE APIs (IMPORTANT 🔥)
def translate_text(text, source, target):
    
    # 🔁 Try Libre APIs first
    urls = [
        "https://translate.argosopentech.com/translate",
        "https://libretranslate.de/translate"
    ]

    payload = {
        "q": text,
        "source": source,
        "target": target,
        "format": "text"
    }

    for url in urls:
        try:
            res = requests.post(url, data=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if "translatedText" in data:
                    return data["translatedText"]
        except:
            continue

    # 🔥 FINAL FALLBACK (Google unofficial API)
    try:
        google_url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl={source}&tl={target}&dt=t&q={text}"
        res = requests.get(google_url)

        if res.status_code == 200:
            result = res.json()
            return result[0][0][0]
    except:
        pass

    return None


@app.post("/translate")
async def translate(text: str = Form(...), source_lang: str = Form(...), target_lang: str = Form(...)):

    source = "auto" if source_lang == "auto" else source_lang

    translated = translate_text(text, source, target_lang)

    if translated:
        return JSONResponse({"translated_text": translated})
    else:
        return JSONResponse({"error": "Translation service unavailable"})