import tornado.ioloop
import tornado.web
from validate import validate_query_params
from tts import text_to_speech 
import hashlib
import os
import time
from collections import defaultdict, deque

AUDIO_DIR = os.path.join(os.getcwd(), "audio")
ASSETS_DIR = os.path.join(os.getcwd(), "assets")

MAX_TEXT_LENGTH = 1000
MAX_AUDIO_AGE_SECONDS = 4 * 60 * 60

MAX_REQ_PER_SECOND = 3
MAX_REQ_PER_MINUTE = 30

# in-memory, per-process rate limit (good enough for single-container deployment)
_recent_requests_1s: dict[str, deque[float]] = defaultdict(deque)
_recent_requests_60s: dict[str, deque[float]] = defaultdict(deque)
# Define a JSON schema for your query parameters
query_param_schema = {
    "type": "object",
    "properties": {
        "text": {"type": "string", "maxLength": MAX_TEXT_LENGTH},
        "speed": {"type": "string", "maxLength": 9},
        "lang": {"type": "string", "enum": ["vi", "en"]},
    },
    "required": ["text", "speed"]
}

class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('web/index.html')

class MyHandler(tornado.web.RequestHandler):
    @validate_query_params(query_param_schema)
    def get(self):
        # Parameters are already validated here
        if not _check_rate_limit(self.request.remote_ip):
            self.set_status(429)
            self.write({"error": "Too Many Requests"})
            return

        text:str = self.get_argument('text')
        speed:str = self.get_argument('speed')
        lang:str = self.get_argument('lang', default='vi')
        current_url:str = '{}://{}'.format(self.request.protocol,self.request.host)
        result,file_name = handle_tts_request(text,speed,lang)
        result["audio_url"] =  current_url+"/audio/"+file_name
        self.write(result)
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

def make_app():
    return tornado.web.Application([
        (r'/', HomeHandler),
        (r"/tts", MyHandler),
        (r'/audio/(.*)', tornado.web.StaticFileHandler, {'path': AUDIO_DIR}),
        (r'/assets/(.*)', tornado.web.StaticFileHandler, {'path': ASSETS_DIR}),
    ])

def _check_rate_limit(remote_ip: str) -> bool:
    if not remote_ip:
        remote_ip = "unknown"
    now = time.time()

    window_1s = _recent_requests_1s[remote_ip]
    while window_1s and (now - window_1s[0]) > 1.0:
        window_1s.popleft()
    if len(window_1s) >= MAX_REQ_PER_SECOND:
        return False

    window_60s = _recent_requests_60s[remote_ip]
    while window_60s and (now - window_60s[0]) > 60.0:
        window_60s.popleft()
    if len(window_60s) >= MAX_REQ_PER_MINUTE:
        return False

    window_1s.append(now)
    window_60s.append(now)
    return True


def _cleanup_old_audio_files():
    cutoff = time.time() - MAX_AUDIO_AGE_SECONDS
    try:
        for name in os.listdir(AUDIO_DIR):
            if not name.endswith(".wav"):
                continue
            path = os.path.join(AUDIO_DIR, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
            except FileNotFoundError:
                pass
    except FileNotFoundError:
        os.makedirs(AUDIO_DIR, exist_ok=True)


def _model_for_lang(lang: str) -> str:
    if lang == "vi":
        return "pretrained_vi.onnx"
    if lang == "en":
        return "pretrained_en_US.onnx"
    return f"pretrained_{lang}.onnx"


def handle_tts_request(text,speed,lang):
    text_hash:str = hashlib.sha1((lang + "|" + text + "|" + speed).encode('utf-8')).hexdigest()
    file_name = text_hash+ ".wav"
    file_path = os.path.join(AUDIO_DIR, file_name)
    if os.path.isfile(file_path):
        return ({
            "hash":text_hash,
            "text":text,
            "speed":speed,
            "lang": lang,
            },file_name)
    else:
        # create new file 
        model_name = _model_for_lang(lang)
        audio_bytes = text_to_speech(text, speed, model_name, text_hash)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(audio_bytes)
        return ({
            "hash":text_hash,
            "text":text,
            "speed":speed,
            "lang": lang,
            },file_name)
    
if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.PeriodicCallback(_cleanup_old_audio_files, 10 * 60 * 1000).start()
    tornado.ioloop.IOLoop.current().start()
