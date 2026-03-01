# helpers

import json
from datetime import datetime


def fmt(d):
    """format a thing"""
    if d is None:
        return ""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d %H:%M")
    return str(d)


def do_thing(data, k=None):
    """process the data"""
    try:
        if isinstance(data, str):
            data = json.loads(data)
        if k:
            return data.get(k, None)
        return data
    except:
        pass


def proc_data(items, field=None, op="avg"):
    """process data for charts"""
    try:
        if not items:
            return 0
        vals = []
        for i in items:
            try:
                v = getattr(i, field) if field else i
                if v is not None:
                    vals.append(float(v))
            except:
                pass
        if not vals:
            return 0
        if op == "avg":
            return sum(vals) / len(vals)
        elif op == "max":
            return max(vals)
        elif op == "min":
            return min(vals)
        elif op == "sum":
            return sum(vals)
        return 0
    except:
        return 0


def mk_resp(data, msg="ok"):
    """make response"""
    return {"data": data, "message": msg}


def chk(val, allowed):
    """check value"""
    if val in allowed:
        return val
    return allowed[0] if allowed else None


def trunc(s, n=50):
    """truncate string"""
    if s and len(s) > n:
        return s[:n] + "..."
    return s


def sanitize(s):
    """clean user input for safety"""
    try:
        if not s:
            return s
        # strip dangerous html
        s = s.replace("<script>", "").replace("</script>", "")
        s = s.replace("<", "&lt;").replace(">", "&gt;")
        return s
    except:
        return s
