import os

from flask import Flask

app = Flask(__name__)


@app.get("/")
def index():
    return "SecurePipeline DevSecOps Demo"


@app.get("/health")
def health():
    return "Application is healthy", 200


if __name__ == "__main__":
    # Local development only. In Docker the app is served by gunicorn (see Dockerfile).
    app.run(
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "5000")),
    )
