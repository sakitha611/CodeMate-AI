from backend.app import create_app
import backend.routes.api as api_routes


def test_smartfix_runs_four_stages_without_executing_code(monkeypatch):
    calls = []

    def fake_ask_ai(task, code="", language="unknown"):
        calls.append((task, code, language))
        if "STAGE 1/4" in task:
            return "Potential division by zero when the list is empty."
        if "STAGE 2/4" in task:
            return "An empty list has no values, so its average is undefined."
        if "STAGE 3/4" in task:
            return "def average(values):\\n    if not values:\\n        return 0\\n    return sum(values) / len(values)"
        return "Static review: the empty-list case is handled. Run unit tests manually."

    monkeypatch.setattr(api_routes, "ask_ai", fake_ask_ai)
    app = create_app()
    app.config.update(TESTING=True)
    response = app.test_client().post(
        "/api/smartfix",
        json={"code": "def average(values): return sum(values) / len(values)", "language": "Python"},
    )

    assert response.status_code == 200
    assert len(calls) == 4
    assert response.json["workflow"] == "Detect → Explain → Fix → Verify"
    assert "if not values" in response.json["fixed_code"]
    assert "not executed" in response.json["verification_type"]


def test_smartfix_requires_code():
    app = create_app()
    app.config.update(TESTING=True)
    response = app.test_client().post("/api/smartfix", json={"code": "  "})
    assert response.status_code == 400
