
import os
import json

from flask import Blueprint, request, jsonify
from flask_login import current_user

from backend.extensions import db
from backend.models import CodeReview
from backend.services.ai_service import ask_ai
from backend.services.security_service import scan


api = Blueprint("api", __name__, url_prefix="/api")


def payload():
    data = request.get_json(silent=True) or {}
    return data


def ai_endpoint(task, default="unknown"):
    data = payload()
    code = (data.get("code") or "").strip()
    language = data.get("language") or default

    if not code and task not in ("Generate code from this request",):
        return jsonify(error="Please provide source code."), 400

    try:
        result = ask_ai(task, code, language)

        if current_user.is_authenticated:
            row = CodeReview(
                user_id=current_user.id,
                kind=task[:40],
                language=language,
                source_code=code or data.get("prompt", ""),
                result=result
            )
            db.session.add(row)
            db.session.commit()

        return jsonify(result=result)

    except Exception as e:
        return jsonify(error=str(e)), 503


@api.post("/review")
def review():
    return ai_endpoint(
        "Review this code. Identify bugs, security issues, performance concerns, "
        "and maintainability issues. Give severity, explanation, and suggested fixes."
    )


@api.post("/debug")
def debug():
    return ai_endpoint(
        "Debug this code. Explain likely root causes and provide corrected code where possible."
    )


@api.post("/security")
def security():
    data = payload()
    code = (data.get("code") or "").strip()

    if not code:
        return jsonify(error="Please provide source code."), 400

    local = scan(code)

    try:
        ai = ask_ai(
            "Perform a security review. Identify vulnerabilities, severity, "
            "affected lines, and mitigations.",
            code,
            data.get("language", "unknown")
        )

        return jsonify(findings=local, analysis=ai)

    except Exception as e:
        return jsonify(
            findings=local,
            warning=str(e),
            analysis="Configure NVIDIA_API_KEY for AI-assisted security analysis."
        )


@api.post("/generate")
def generate():
    data = payload()
    prompt = (data.get("prompt") or "").strip()

    if not prompt:
        return jsonify(error="Describe what code you want to generate."), 400

    try:
        result = ask_ai(
            "Generate code for this request: " + prompt,
            "",
            data.get("language", "Python")
        )
        return jsonify(result=result)

    except Exception as e:
        return jsonify(error=str(e)), 503


@api.post("/fix")
def fix():
    return ai_endpoint(
        "Fix the supplied code. Return the complete corrected code first, "
        "then briefly explain the changes."
    )


@api.post("/smartfix")
def smartfix():
    """Run a guided, multi-stage AI code-improvement workflow."""

    data = payload()
    code = (data.get("code") or "").strip()
    language = data.get("language") or "unknown"

    if not code:
        return jsonify(error="Please provide source code."), 400

    try:
        diagnosis = ask_ai(
            "BUGZERO STAGE 1/4 — DETECT. Inspect the supplied code for bugs, "
            "edge cases, and likely runtime errors. List the most important "
            "findings with severity and explain what may go wrong. Do not claim "
            "you executed the code.",
            code,
            language,
        )

        explanation = ask_ai(
            "BUGZERO STAGE 2/4 — EXPLAIN. Explain the findings below in clear, "
            "beginner-friendly language. Explain why each issue matters and "
            "which input or condition can trigger it. Do not claim execution.\n\n"
            f"Findings:\n{diagnosis}",
            code,
            language,
        )

        fixed_code = ask_ai(
            "BUGZERO STAGE 3/4 — FIX. Return the complete corrected source code "
            "only. Do not use Markdown fences and do not include explanations "
            "outside the code. Preserve the original purpose and language. "
            "If the code is already sound, return it unchanged. Do not claim "
            "that you ran it. Use these findings as context:\n\n"
            f"{diagnosis}\n\nExplanation:\n{explanation}",
            code,
            language,
        ).strip()

        verification = ask_ai(
            "BUGZERO STAGE 4/4 — VERIFY BY REVIEW. Review the proposed corrected "
            "code for remaining bugs, edge cases, and consistency with the "
            "original purpose. State clearly that this is a static AI review, "
            "not execution or test results. Mention any manual tests the user "
            "should run.\n\nOriginal code:\n"
            f"{code}\n\nProposed corrected code:\n{fixed_code}",
            fixed_code,
            language,
        )

        if current_user.is_authenticated:
            row = CodeReview(
                user_id=current_user.id,
                kind="BugZero Intelligence",
                language=language,
                source_code=code,
                result=(
                    "DETECT\n" + diagnosis
                    + "\n\nEXPLAIN\n" + explanation
                    + "\n\nFIX\n" + fixed_code
                    + "\n\nVERIFY\n" + verification
                ),
            )

            db.session.add(row)
            db.session.commit()

        return jsonify(
            workflow="Detect → Explain → Fix → Verify",
            diagnosis=diagnosis,
            explanation=explanation,
            fixed_code=fixed_code,
            verification=verification,
            verification_type="AI static review; code was not executed.",
        )

    except Exception as e:
        return jsonify(error=str(e)), 503


@api.post("/tests/generate")
def tests():
    return ai_endpoint(
        "Generate useful unit tests for this code, including edge cases. "
        "State the testing framework and provide test code."
    )


@api.post("/chat")
def chat():
    data = payload()
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify(error="Enter a message."), 400

    try:
        result = ask_ai(
            message,
            data.get("code", ""),
            data.get("language", "unknown")
        )
        return jsonify(result=result)

    except Exception as e:
        return jsonify(error=str(e)), 503


@api.get("/history")
def history():
    if not current_user.is_authenticated:
        return jsonify(error="Please log in to view history."), 401

    rows = (
        CodeReview.query
        .filter_by(user_id=current_user.id)
        .order_by(CodeReview.created_at.desc())
        .limit(100)
        .all()
    )

    return jsonify(
        items=[
            {
                "id": r.id,
                "kind": r.kind,
                "language": r.language,
                "created_at": r.created_at.isoformat(),
                "result": r.result
            }
            for r in rows
        ]
    )


@api.delete("/history/<int:item_id>")
def delete_history(item_id):
    if not current_user.is_authenticated:
        return jsonify(error="Please log in."), 401

    row = CodeReview.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(row)
    db.session.commit()

    return jsonify(ok=True)


@api.get("/github/repositories")
def github_repositories():
    import requests

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        return jsonify(
            error="Configure GITHUB_TOKEN on the server first."
        ), 503

    response = requests.get(
        "https://api.github.com/user/repos",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        },
        timeout=15
    )

    if not response.ok:
        return jsonify(
            error="GitHub API request failed.",
            details=response.text[:300]
        ), response.status_code

    return jsonify(
        repositories=[
            {
                "name": r["full_name"],
                "url": r["html_url"],
                "private": r["private"]
            }
            for r in response.json()
        ]
    )
