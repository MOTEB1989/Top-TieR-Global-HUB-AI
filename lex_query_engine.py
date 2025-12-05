"""Safe querying helpers for Lex knowledge items stored in Neo4j."""
from __future__ import annotations

from typing import Dict, List, Optional

from py2neo import Graph


class LexQueryEngine:
    """Query Lex knowledge items by context category.

    Parameters
    ----------
    neo4j_url:
        Bolt URL for the Neo4j instance.
    user:
        Username for Neo4j authentication.
    password:
        Password for Neo4j authentication.
    graph:
        Optional pre-configured :class:`py2neo.Graph` instance for testing.
    """

    def __init__(
        self, neo4j_url: str, user: str, password: str, graph: Optional[Graph] = None
    ) -> None:
        self.graph = graph or Graph(neo4j_url, auth=(user, password))

    def query_by_context(self, context: str, top_k: int = 3) -> List[Dict[str, str]]:
        """Return knowledge items whose category contains the provided context.

        The method uses parameterized Cypher to avoid injection issues and enforces
        a positive ``top_k`` value.
        """

        if not context:
            return []

        if top_k < 1:
            raise ValueError("top_k must be a positive integer")

        query = """
        MATCH (k:KnowledgeItem)
        WHERE toLower(k.category) CONTAINS $context
        RETURN k.id AS id, k.title AS title, k.content AS content, k.category AS category, k.source AS source, k.url AS url
        LIMIT $top_k
        """

        normalized_context = context.strip().lower()
        return self.graph.run(
            query, context=normalized_context, top_k=top_k
        ).data()


if __name__ == "__main__":
    engine = LexQueryEngine(
        neo4j_url="bolt://localhost:7687", user="neo4j", password="your_password"
    )

    context = "شرعي"  # يمكن أن يكون: شرعي، نظامي، لغوي، أدبي...
    top_items = engine.query_by_context(context)

    for item in top_items:
        print(f"[{item['category']}] {item['title']}\n{item['content']}\n---")
