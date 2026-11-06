# py-svc

Python 3.11 + FastAPI internal text analysis service. It listens only on `127.0.0.1` and logs to stdout/stderr.

## Setup and run

From this directory in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
$env:PORT = "5102"
$env:INTERNAL_TOKEN = "dev-token"
$env:DATA_DIR = ".\.devdata"
python main.py
```

`PORT` must be an integer from 1 to 65535. `INTERNAL_TOKEN` and `DATA_DIR` are also required. Invalid or missing settings print an error to stderr and exit with code 2. The service creates `DATA_DIR` if it does not exist.

Run tests with `python -m pytest`. While the service is running, run `./tests/smoke-py.ps1` from PowerShell.

## Endpoints

- `GET /health` is public and returns `{"status":"ok","service":"py-svc"}`.
- `POST /shutdown` requires `X-Internal-Token` and requests graceful Uvicorn shutdown.
- `POST /analyze` requires `X-Internal-Token` and a JSON body such as `{"text":"Hello world."}`. Empty/whitespace text returns 400; text over 100,000 characters returns 413. Successful responses include `charCount`, `wordCount`, `sentenceCount`, and up to ten `topKeywords` after basic stopword filtering.
- Invalid or missing internal tokens return 401.

Sentence counts use simple punctuation/newline splitting. For Thai, `pythainlp` is installed and used for word segmentation. If it cannot be imported at runtime, the fallback splits on whitespace (with basic Unicode token extraction), so Thai phrases without spaces will not have linguistically accurate word counts or keywords. Stopwords are intentionally a small built-in list, not a comprehensive language model.
