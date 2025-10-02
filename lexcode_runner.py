# -*- coding: utf-8 -*-
"""
LexCode Runner — نسخة شاملة
يدعم:
- fetch: postgres, github.repo (محلي), redis, neo4j
- process: gpt-*, huggingface/<model-name> (Embeddings)
- render: web.table, web.list, db.store (neo4j / redis / postgres / sqlite), web.save_html

الإعداد عبر متغيرات البيئة (انظر أسفل الملف).
"""

import os, sys, json, time, hashlib, yaml, logging
from pprint import pprint
from typing import Any, Dict, List

# ---------- لواحق اختيارية بحسب الخطوات ----------
# OpenAI
try:
    import openai  # ملاحظة: تستخدم ChatCompletion API الكلاسيكي
except Exception:
    openai = None

# Postgres
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:
    psycopg2 = None

# Redis
try:
    import redis
except Exception:
    redis = None

# Neo4j
try:
    from neo4j import GraphDatabase
except Exception:
    GraphDatabase = None

# HuggingFace (Embeddings)
try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None

# ---------------------------------------------------

LOG_LEVEL = os.getenv("LEXCODE_LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s | %(levelname)s | %(message)s",
)
log = logging.getLogger("lexcode-runner")


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


class LexCodeRunner:
    def __init__(self, recipe_file: str = "lexcode.yml"):
        if not os.path.exists(recipe_file):
            raise FileNotFoundError(f"لم أجد ملف الوصفة: {recipe_file}")
        with open(recipe_file, "r", encoding="utf-8") as f:
            self.recipe = yaml.safe_load(f)
        # OpenAI
        self.openai_key = os.getenv("OPENAI_API_KEY") or os.getenv("LEXCODE_OPENAI_KEY")
        if openai and self.openai_key:
            openai.api_key = self.openai_key

        log.info("🧠 Loaded recipe for project: %s", self.recipe.get("project"))

    # ------------- واجهة التشغيل الرئيسية -------------
    def run(self):
        print(f"🚀 Running LexCode project: {self.recipe.get('project')}")
        for task in self.recipe.get("tasks", []):
            tname = task.get("name", task.get("id", "unnamed"))
            print(f"\n▶️ Task: {tname}")
            result = None
            for step in task.get("steps", []):
                if "fetch" in step:
                    result = self._fetch(step["fetch"])
                elif "process" in step:
                    result = self._process(result, step["process"])
                elif "render" in step:
                    self._render(result, step["render"])
                else:
                    log.warning("خطوة غير معروفة: %s", list(step.keys()))
            print(f"✅ Finished task: {tname}")

    # --------------------- FETCH ---------------------
    def _fetch(self, config: Dict[str, Any]):
        source = config.get("source")
        log.info("📥 FETCH from source=%s", source)

        if source == "postgres":
            if not psycopg2:
                raise RuntimeError("psycopg2 غير مثبت. أضِفه إلى requirements.")
            # اتصال عبر DB_URL أو متغيرات PG_*
            db_url = os.getenv("DB_URL")
            if db_url:
                conn = psycopg2.connect(db_url)
            else:
                conn = psycopg2.connect(
                    host=os.getenv("PG_HOST", "localhost"),
                    dbname=os.getenv("PG_DB", "postgres"),
                    user=os.getenv("PG_USER", "postgres"),
                    password=os.getenv("PG_PASS", "postgres"),
                    port=int(os.getenv("PG_PORT", "5432")),
                )
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute(config["query"])
            rows = cur.fetchall()
            cur.close(); conn.close()
            log.info("📥 Fetched %d rows from Postgres", len(rows))
            return rows

        elif source == "github.repo":
            # قراءة ملفات محلية من المسار المحدد (بسيط وسريع)
            path = config.get("path", "docs/")
            files = []
            for root, _, filenames in os.walk(path):
                for fn in filenames:
                    p = os.path.join(root, fn)
                    try:
                        with open(p, "r", encoding="utf-8", errors="ignore") as f:
                            files.append({"path": p, "content": f.read()})
                    except Exception as e:
                        log.warning("تخطي %s: %s", p, e)
            log.info("📥 Loaded %d files from %s", len(files), path)
            return files

        elif source == "redis":
            if not redis:
                raise RuntimeError("redis-py غير مثبت. أضِفه إلى requirements.")
            r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            pattern = config.get("pattern", "lexcode:*")
            out = []
            for key in r.scan_iter(match=pattern):
                try:
                    val = r.get(key)
                    out.append({"key": key.decode() if isinstance(key, bytes) else key,
                                "value": val.decode() if isinstance(val, bytes) else val})
                except Exception as e:
                    log.warning("Redis read error for %s: %s", key, e)
            log.info("📥 Fetched %d entries from Redis (pattern=%s)", len(out), pattern)
            return out

        elif source == "neo4j":
            if not GraphDatabase:
                raise RuntimeError("neo4j-driver غير مثبت. أضِفه إلى requirements.")
            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            pwd = os.getenv("NEO4J_PASS", "neo4j")
            query = config.get("query", "MATCH (n) RETURN n LIMIT 10")
            with GraphDatabase.driver(uri, auth=(user, pwd)) as drv:
                with drv.session() as s:
                    res = s.run(query)
                    rows = [r.data() for r in res]
            log.info("📥 Fetched %d records from Neo4j", len(rows))
            return rows

        else:
            log.warning("⚠️ Unknown fetch source: %s", source)
            return None

    # -------------------- PROCESS --------------------
    def _process(self, data: Any, config: Dict[str, Any]):
        model = config.get("model", "")
        op = config.get("operation", "chat")
        log.info("🧠 PROCESS with model=%s op=%s", model, op)

        # GPT-* (OpenAI chat)
        if model.startswith("gpt"):
            if not openai or not self.openai_key:
                raise RuntimeError("openai غير مثبت أو OPENAI_API_KEY غير مخصص.")
            prompt = config.get("prompt", "حلل البيانات التالية وأعطني مخرجات منظمة:")
            # ادمج البيانات كنص
            user_content = f"{prompt}\n\n{json.dumps(data, ensure_ascii=False)[:120000]}"
            resp = openai.ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": user_content}],
                temperature=0.2,
            )
            output = resp["choices"][0]["message"]["content"]
            log.info("🤖 GPT processed data")
            return output

        # HuggingFace Embeddings: model = "huggingface/<model-name>"
        if model.startswith("huggingface/"):
            if not SentenceTransformer:
                raise RuntimeError("sentence-transformers غير مثبت.")
            hf_model = model.split("/", 1)[-1]  # e.g. "all-MiniLM-L6-v2"
            st = SentenceTransformer(hf_model)
            texts: List[str]
            if isinstance(data, list):
                # حاول استخراج نص من عناصر متنوعة
                texts = [
                    (d if isinstance(d, str) else json.dumps(d, ensure_ascii=False))
                    for d in data
                ]
            else:
                texts = [data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)]
            emb = st.encode(texts, normalize_embeddings=True).tolist()
            log.info("🔡 HF embeddings generated for %d item(s)", len(texts))
            return emb

        log.warning("⚠️ Unsupported model: %s", model)
        return data

    # -------------------- RENDER ---------------------
    def _render(self, data: Any, config: Dict[str, Any]):
        rtype = config.get("type")
        options = config.get("options", {}) or {}
        log.info("🖼  RENDER type=%s", rtype)

        if rtype == "web.table":
            title = options.get("title", "Table")
            cols = options.get("columns")
            print(f"\n=== {title} ===")
            if cols and isinstance(data, list) and data and isinstance(data[0], dict):
                # اطبع جدول مبسط
                header = " | ".join(cols)
                print(header)
                print("-" * len(header))
                for row in data:
                    print(" | ".join(str(row.get(c)) for c in cols))
            else:
                pprint(data)

        elif rtype == "web.list":
            title = options.get("title", "List")
            print(f"\n=== {title} ===")
            if isinstance(data, list):
                for i, item in enumerate(data, 1):
                    print(f"{i}. {str(item)[:500]}")
            else:
                print(str(data)[:1000])

        elif rtype == "web.save_html":
            # يخزن مخرجات كملف HTML بسيط لعرضها من أي واجهة
            out_dir = options.get("out_dir", "out")
            os.makedirs(out_dir, exist_ok=True)
            fname = options.get("filename", f"report_{int(time.time())}.html")
            path = os.path.join(out_dir, fname)
            html = f"""<!doctype html><meta charset="utf-8">
            <h1>{options.get('title','LexCode Report')}</h1>
            <pre style="white-space:pre-wrap">{json.dumps(data, ensure_ascii=False, indent=2)}</pre>
            """
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"🌐 Saved HTML report → {path}")

        elif rtype == "db.store":
            target = options.get("database", "sqlite")
            if target == "neo4j":
                self._store_neo4j(data, options)
            elif target == "redis":
                self._store_redis(data, options)
            elif target == "postgres":
                self._store_postgres(data, options)
            elif target == "sqlite":
                self._store_sqlite(data, options)
            else:
                log.warning("⚠️ Unknown DB target: %s", target)

        else:
            log.warning("⚠️ Unknown render type: %s", rtype)

    # -------------------- STORE HELPERS --------------------
    def _store_neo4j(self, data: Any, options: Dict[str, Any]):
        if not GraphDatabase:
            raise RuntimeError("neo4j-driver غير مثبت.")
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        pwd = os.getenv("NEO4J_PASS", "neo4j")
        label = options.get("label", "Chunk")
        relation = options.get("relation", None)  # مثال: "KNOWS"
        namespace = options.get("namespace", "default")
        items = data if isinstance(data, list) else [data]

        with GraphDatabase.driver(uri, auth=(user, pwd)) as drv:
            with drv.session() as s:
                for item in items:
                    text = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
                    h = sha1(text)
                    s.run(
                        f"MERGE (d:{label} {{id:$id}}) "
                        "ON CREATE SET d.text=$text, d.namespace=$ns, d.ts=timestamp()",
                        id=h, text=text, ns=namespace
                    )
                if relation:
                    # علاقة بسيطة بين كل عناصر السجل (سلاسل)
                    ids = [sha1(i if isinstance(i, str) else json.dumps(i, ensure_ascii=False)) for i in items]
                    for i in range(len(ids)-1):
                        s.run(
                            f"MATCH (a:{label} {{id:$a}}),(b:{label} {{id:$b}}) "
                            f"MERGE (a)-[:{relation}]->(b)", a=ids[i], b=ids[i+1]
                        )
        print(f"💾 Stored {len(items)} item(s) into Neo4j label={label} ns={namespace}")

    def _store_redis(self, data: Any, options: Dict[str, Any]):
        if not redis:
            raise RuntimeError("redis-py غير مثبت.")
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        prefix = options.get("key_prefix", "lexcode:out")
        items = data if isinstance(data, list) else [data]
        n = 0
        for item in items:
            text = item if isinstance(item, str) else json.dumps(item, ensure_ascii=False)
            k = f"{prefix}:{sha1(text)}"
            r.set(k, text)
            n += 1
        print(f"💾 Stored {n} item(s) into Redis with prefix={prefix}")

    def _store_postgres(self, data: Any, options: Dict[str, Any]):
        if not psycopg2:
            raise RuntimeError("psycopg2 غير مثبت.")
        db_url = os.getenv("DB_URL")
        if db_url:
            conn = psycopg2.connect(db_url)
        else:
            conn = psycopg2.connect(
                host=os.getenv("PG_HOST", "localhost"),
                dbname=os.getenv("PG_DB", "postgres"),
                user=os.getenv("PG_USER", "postgres"),
                password=os.getenv("PG_PASS", "postgres"),
                port=int(os.getenv("PG_PORT", "5432")),
            )
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS lexcode_results (id SERIAL PRIMARY KEY, payload JSONB, created_at TIMESTAMP DEFAULT NOW())")
        payload = json.dumps(data, ensure_ascii=False)
        cur.execute("INSERT INTO lexcode_results (payload) VALUES (%s)", (payload,))
        conn.commit(); cur.close(); conn.close()
        print("💾 Stored results into Postgres table=lexcode_results")

    def _store_sqlite(self, data: Any, options: Dict[str, Any]):
        import sqlite3
        out_dir = options.get("out_dir", "out")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, options.get("db_name", "runner_output.db"))
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS results (id INTEGER PRIMARY KEY AUTOINCREMENT, payload TEXT)")
        cur.execute("INSERT INTO results (payload) VALUES (?)", (json.dumps(data, ensure_ascii=False),))
        conn.commit(); conn.close()
        print(f"💾 Stored results into SQLite → {path}")


# ---------------------- تشغيل مباشر ----------------------
if __name__ == "__main__":
    recipe_path = sys.argv[1] if len(sys.argv) > 1 else "lexcode.yml"
    runner = LexCodeRunner(recipe_path)
    runner.run()


