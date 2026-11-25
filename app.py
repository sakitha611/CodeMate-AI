import os
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_login import current_user
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

from backend.config import Config
from backend.extensions import db, login_manager
from backend.models import User
from backend.routes.api import api
from backend.routes.auth import auth

def create_app():
    app=Flask(__name__,static_folder=str(ROOT/"frontend"),static_url_path="/static")
    app.config.from_object(Config)
    db.init_app(app); login_manager.init_app(app)
    @login_manager.user_loader
    def load_user(user_id): return db.session.get(User,int(user_id))
    app.register_blueprint(api); app.register_blueprint(auth)
    @app.get("/")
    def home(): return send_from_directory(ROOT/"frontend","index.html")
    @app.get("/app")
    def dashboard(): return send_from_directory(ROOT/"frontend","app.html")
    @app.get("/health")
    def health(): return jsonify(status="ok",service="BUGZERO AI")
    with app.app_context():
        (ROOT/"database").mkdir(exist_ok=True)
        db.create_all()
    return app

app=create_app()
if __name__=="__main__":
    app.run(host="127.0.0.1",port=int(os.getenv("PORT",5000)),debug=os.getenv("FLASK_DEBUG")=="1")
