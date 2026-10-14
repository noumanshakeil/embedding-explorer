# Dev server for embedding-explorer
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
