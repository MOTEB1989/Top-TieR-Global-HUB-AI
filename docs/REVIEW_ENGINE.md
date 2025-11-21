# Review Engine

The review engine provides unified analysis pipelines for code, security, and document content while delegating LLM work to the gateway layer.

## Modules

- `review_engine.reviewer.ReviewEngine` — dispatches review requests to specialized modules and normalizes responses.
- `review_engine.code_review` — combines static code checks (unused imports, dangerous patterns, missing error handling) with LLM reasoning.
- `review_engine.security_review` — detects secrets, insecure patterns, and uses the LLM for deeper analysis.
- `review_engine.document_review` — performs clarity/completeness checks and requests LLM summaries.
- `review_engine.llm_review` — shared prompt construction and gateway integration.

## Usage

```python
from review_engine.reviewer import ReviewEngine

engine = ReviewEngine()
result = engine.run(
    review_type="code",
    input_text="""
    import os
    
    def run(cmd):
        return os.system(cmd)
    """,
    metadata={"service": "api"},
)
print(result)
```

### CLI

You can trigger the engine directly from the command line:

```bash
python -m review_engine.reviewer --type code --content "def hello():\n    print('hi')"
```

The output is a normalized dictionary with keys:
`summary`, `findings`, `risk_level`, `recommendations`, `provider`, `model`, `raw`.
