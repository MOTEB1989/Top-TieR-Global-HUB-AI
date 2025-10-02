# Adapter Examples Library

This directory contains self-contained examples that demonstrate how to
connect to common APIs and databases across multiple languages.  The
structure mirrors the four pillars outlined in the roadmap:

- **Programming APIs** – request helpers for Python, Node.js, and Rust.
- **Database APIs** – ready-to-run snippets for popular data stores.
- **Web Framework APIs** – Express example showcasing REST patterns.
- **Security & Integrations** – GitHub OAuth device flow helper.

Each adapter is intentionally lightweight so teams can copy, extend, or
wire them into prototypes quickly.  Dependencies that are not part of
this repository are treated as optional; the examples emit descriptive
errors when packages such as database drivers are missing.
