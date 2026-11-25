from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.extensions import db
from backend.models import User
auth=Blueprint("auth",__name__,url_prefix="/api/auth")

@auth.post("/register")
def register():
    d=request.get_json(silent=True) or {}
    username=(d.get("username") or "").strip()
    email=(d.get("email") or "").strip().lower()
    password=d.get("password") or ""
    if not username or "@" not in email or len(password)<8:
        return jsonify(error="Enter a username, valid email, and password with at least 8 characters."),400
    if User.query.filter_by(email=email).first(): return jsonify(error="Email already registered."),409
    user=User(username=username,email=email); user.set_password(password)
    db.session.add(user); db.session.commit(); login_user(user)
    return jsonify(ok=True,user={"username":user.username,"email":user.email}),201

@auth.post("/login")
def login():
    d=request.get_json(silent=True) or {}; email=(d.get("email") or "").lower().strip()
    user=User.query.filter_by(email=email).first()
    if not user or not user.check_password(d.get("password") or ""):
        return jsonify(error="Invalid email or password."),401
    login_user(user); return jsonify(ok=True,user={"username":user.username,"email":user.email})

@auth.post("/logout")
@login_required
def logout():
    logout_user(); return jsonify(ok=True)

@auth.get("/profile")
def profile():
    if not current_user.is_authenticated: return jsonify(authenticated=False)
    return jsonify(authenticated=True,user={"username":current_user.username,"email":current_user.email})
