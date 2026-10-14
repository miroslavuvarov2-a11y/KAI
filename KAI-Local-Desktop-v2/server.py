from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, urllib.request, urllib.error

HOST, PORT = "127.0.0.1", 8790
OLLAMA, DEFAULT_MODEL = "http://127.0.0.1:11434", "qwen3:4b"

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args): print("[KAI] " + (fmt % args))
    def send_json(self, status, data):
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)
    def do_GET(self):
        if self.path == "/api/status":
            try:
                req = urllib.request.Request(OLLAMA + "/api/tags")
                with urllib.request.urlopen(req, timeout=3) as res: payload = json.loads(res.read().decode("utf-8"))
                self.send_json(200, {"ok":True,"ollama":True,"models":[m.get("name","") for m in payload.get("models",[])],"default_model":DEFAULT_MODEL})
            except Exception as exc:
                self.send_json(200, {"ok":True,"ollama":False,"models":[],"default_model":DEFAULT_MODEL,"error":str(exc)})
            return
        if self.path in ("/", "/index.html"):
            try:
                with open("index.html","rb") as f: body=f.read()
                self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8")
                self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
            except OSError: self.send_error(500,"index.html not found")
            return
        self.send_error(404)
    def do_POST(self):
        if self.path != "/api/chat": self.send_error(404); return
        try:
            size=int(self.headers.get("Content-Length","0"))
            if size <= 0 or size > 1000000: self.send_json(400,{"error":"Некорректный размер запроса."}); return
            data=json.loads(self.rfile.read(size).decode("utf-8"))
            messages=data.get("messages",[]); model=data.get("model") or DEFAULT_MODEL
            if not isinstance(messages,list) or not messages: self.send_json(400,{"error":"Напиши сообщение."}); return
            clean=[]
            for item in messages[-24:]:
                role=item.get("role"); content=item.get("content","")
                if role in ("user","assistant") and isinstance(content,str): clean.append({"role":role,"content":content[:12000]})
            payload=json.dumps({"model":model,"messages":clean,"stream":False,"think":False}).encode("utf-8")
            req=urllib.request.Request(OLLAMA+"/api/chat",data=payload,headers={"Content-Type":"application/json"},method="POST")
            with urllib.request.urlopen(req,timeout=240) as res: answer=json.loads(res.read().decode("utf-8"))
            self.send_json(200,{"reply":answer.get("message",{}).get("content","").strip() or "Модель вернула пустой ответ."})
        except urllib.error.HTTPError as exc:
            self.send_json(502,{"error":"Ollama ответила ошибкой: "+exc.read().decode("utf-8",errors="replace")[:1000]})
        except Exception as exc:
            self.send_json(502,{"error":"Не удалось получить ответ от локального ИИ. Проверь Ollama и модель.","detail":str(exc)})

if __name__ == "__main__":
    print("KAI Local Desktop: http://127.0.0.1:" + str(PORT))
    print("Окно не закрывай, пока пользуешься приложением.")
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
