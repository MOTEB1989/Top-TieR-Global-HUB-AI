import json
import sqlite3


def handle_render(config, data):
    rtype = config.get("type")

    if rtype == "web.table":
        print(f"🌐 Rendering table: {config['options']['title']}")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if rtype == "web.list":
        print(f"🌐 Rendering list: {config['options']['title']}")
        for item in data[:5]:
            print("-", item)
        return

    if rtype == "db.store":
        db = config["options"]["database"]
        if db == "neo4j":
            print("🗃️ Storing in Neo4j (pseudo-code here)")
            return
        if db == "sqlite":
            conn = sqlite3.connect("output.db")
            cur = conn.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS results (data TEXT)")
            cur.execute("INSERT INTO results (data) VALUES (?)", (json.dumps(data),))
            conn.commit()
            conn.close()
            print("💾 Stored results in SQLite")
            return

    print(f"⚠️ Unknown render type: {rtype}")
