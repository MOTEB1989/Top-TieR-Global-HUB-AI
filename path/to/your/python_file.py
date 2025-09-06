try:
    data = fut.result()
    if isinstance(data, list):
        res.extend(data)
    else:
        res.append({"error": "Invalid data type", "data": data})
except Exception as e:
    res.append({"source": futs[fut], "error": str(e), "ts": now_iso()})
