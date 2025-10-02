import json
import os
import sqlite3


def handle_render(config, data):
    rtype = config.get("type")
    opts = config.get("options", {})

    if rtype == "web.table":
        title = opts.get("title", "Table")
        cols = opts.get("columns", [])
        print(f"🌐 Render Table: {title}")
        print("Columns:", cols)
        print(json.dumps(data, ensure_ascii=False, indent=2))

    elif rtype == "web.list":
        title = opts.get("title", "List")
        print(f"🌐 Render List: {title}")
        items = data if isinstance(data, list) else [data]
        for i, item in enumerate(items[:20], 1):
            print(f"{i}. {str(item)[:500]}")

    elif rtype == "db.store":
        target = opts.get("database", "sqlite")
        if target == "sqlite":
            os.makedirs("/app/out", exist_ok=True)
            db_path = "/app/out/runner_output.db"
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT)"
            )
            cur.execute(
                "INSERT INTO results (payload) VALUES (?)",
                (json.dumps(data, ensure_ascii=False),),
            )
            conn.commit()
            conn.close()
            print(f"💾 Stored results in SQLite at {db_path}")
        elif target == "neo4j":
            print("🗃️ TODO: integrate neo4j-driver here")
        else:
            print(f"⚠️ Unknown DB target: {target}")

    else:
        print(f"⚠️ Unknown render type: {rtype}")
