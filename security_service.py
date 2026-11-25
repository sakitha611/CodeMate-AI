import re

PATTERNS = [
    ("Possible hardcoded secret", r"(?i)(api[_-]?key|password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]", "high"),
    ("Possible SQL injection", r"(?i)(execute|query)\s*\(\s*f['\"]|\.format\s*\(", "high"),
    ("Potential unsafe eval", r"\beval\s*\(", "high"),
    ("Potential shell command injection", r"(?i)(shell\s*=\s*True|os\.system\s*\()", "medium"),
]

def scan(code):
    findings=[]
    for title, pattern, severity in PATTERNS:
        for m in re.finditer(pattern, code):
            line=code.count("\\n",0,m.start())+1
            findings.append({"title":title,"severity":severity,"line":line,
                             "evidence":code.splitlines()[line-1][:240],
                             "recommendation":"Review this code path and use a safer, parameterized or secret-managed alternative."})
    return findings
