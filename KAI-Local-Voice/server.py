import base64, io, json, os, platform, subprocess, webbrowser
from pathlib import Path
import httpx, pyautogui
from fastapi import FastAPI
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()
MODEL = os.getenv("KAI_MODEL", "qwen3:4b")
OLLAMA_CHAT = "http://127.0.0.1:11434/api/chat"

SYSTEM = """Ты KAI — локальный голосовой помощник Windows.
Отвечай по-русски, коротко и естественно.
Если пользователь просит выполнить действие на компьютере, используй доступные инструменты.
Не утверждай, что действие выполнено, пока инструмент не вернул успешный результат.
Не удаляй файлы и не выполняй произвольные команды cmd, PowerShell или shell.
"""

TOOLS = [
 {"type":"function","function":{"name":"computer_status","description":"Получить базовую информацию о компьютере.","parameters":{"type":"object","properties":{},"additionalProperties":False}}},
 {"type":"function","function":{"name":"screenshot","description":"Сделать скриншот текущего экрана.","parameters":{"type":"object","properties":{},"additionalProperties":False}}},
 {"type":"function","function":{"name":"open_url","description":"Открыть сайт HTTP или HTTPS.","parameters":{"type":"object","properties":{"url":{"type":"string"}},"required":["url"],"additionalProperties":False}}},
 {"type":"function","function":{"name":"open_app","description":"Открыть разрешённое приложение Windows.","parameters":{"type":"object","properties":{"app":{"type":"string","enum":["notepad","calculator","explorer"]}},"required":["app"],"additionalProperties":False}}},
 {"type":"function","function":{"name":"open_folder","description":"Открыть существующую папку Windows.","parameters":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"],"additionalProperties":False}}},
 {"type":"function","function":{"name":"move_mouse","description":"Переместить мышь.","parameters":{"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"}},"required":["x","y"],"additionalProperties":False}}},
 {"type":"function","function":{"name":"click","description":"Нажать кнопку мыши.","parameters":{"type":"object","properties":{"x":{"type":"integer"},"y":{"type":"integer"},"button":{"type":"string","enum":["left","right","middle"]}},"required":["x","y","button"],"additionalProperties":False}}},
 {"type":"function","function":{"name":"type_text","description":"Напечатать текст в активном окне.","parameters":{"type":"object","properties":{"text":{"type":"string","maxLength":1000}},"required":["text"],"additionalProperties":False}}},
 {"type":"function","function":{"name":"press_key","description":"Нажать разрешённую клавишу.","parameters":{"type":"object","properties":{"key":{"type":"string"}},"required":["key"],"additionalProperties":False}}}
]

def run_tool(name,args):
    if name=="computer_status":
        return {"ok":True,"os":platform.platform(),"computer":platform.node()}
    if name=="screenshot":
        image=pyautogui.screenshot(); b=io.BytesIO(); image.save(b,"PNG")
        return {"ok":True,"image_base64":base64.b64encode(b.getvalue()).decode()}
    if name=="open_url":
        url=args["url"]
        if not url.startswith(("http://","https://")): return {"ok":False,"error":"Разрешены только HTTP/HTTPS URL."}
        webbrowser.open(url); return {"ok":True}
    if name=="open_app":
        commands={"notepad":["notepad.exe"],"calculator":["calc.exe"],"explorer":["explorer.exe"]}
        subprocess.Popen(commands[args["app"]]); return {"ok":True}
    if name=="open_folder":
        path=Path(args["path"]).expanduser().resolve()
        if not path.is_dir(): return {"ok":False,"error":"Папка не существует."}
        os.startfile(str(path)); return {"ok":True,"path":str(path)}
    if name=="move_mouse":
        pyautogui.moveTo(args["x"],args["y"],duration=0.15); return {"ok":True}
    if name=="click":
        pyautogui.click(args["x"],args["y"],button=args["button"]); return {"ok":True}
    if name=="type_text":
        pyautogui.write(args["text"],interval=0.01); return {"ok":True}
    if name=="press_key":
        key=args["key"].lower()
        allowed={"enter","esc","tab","space","backspace","delete","home","end","up","down","left","right","ctrl","alt","shift","win","f1","f2","f3","f4","f5","f6","f7","f8","f9","f10","f11","f12"}
        if key not in allowed and len(key)!=1: return {"ok":False,"error":"Эта клавиша запрещена."}
        pyautogui.press(key); return {"ok":True}
    return {"ok":False,"error":"Неизвестный инструмент."}

@app.get("/")
def home(): return FileResponse("web/index.html")

@app.get("/health")
async def health():
    try:
        async with httpx.AsyncClient(timeout=3) as client:
            r=await client.get("http://127.0.0.1:11434/api/tags")
        return {"ollama":r.status_code==200,"model":MODEL}
    except Exception:
        return {"ollama":False,"model":MODEL}

@app.post("/chat")
async def chat(body:dict):
    messages=[{"role":"system","content":SYSTEM}]
    messages.extend(body.get("messages",[]))
    for _ in range(6):
        async with httpx.AsyncClient(timeout=180) as client:
            r=await client.post(OLLAMA_CHAT,json={"model":MODEL,"messages":messages,"tools":TOOLS,"stream":False})
        if r.status_code>=400: return {"text":"Ошибка Ollama: "+r.text}
        message=r.json().get("message",{})
        messages.append(message)
        calls=message.get("tool_calls",[])
        if not calls: return {"text":message.get("content","")}
        for call in calls:
            fn=call["function"]
            result=run_tool(fn["name"],fn.get("arguments",{}))
            messages.append({"role":"tool","content":json.dumps(result,ensure_ascii=False)})
    return {"text":"Не удалось завершить действие за отведённое число шагов."}

if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8790)
