APP_TITLE = "Youi RAG API"
HOST = "0.0.0.0"
PORT = 3456

# Chat memory kept on the server
MAX_HISTORY = 5       # turns passed to the model per question
MAX_SESSIONS = 1000   # oldest session is dropped beyond this

# CORS
CORS_ORIGINS = ["*"]
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]
