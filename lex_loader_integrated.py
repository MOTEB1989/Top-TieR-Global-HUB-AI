"""Utility to load Lex Supreme knowledge items from YAML into Neo4j.

Usage example:
    python lex_loader_integrated.py \
        --yaml-path data/lex_supreme_knowledge_base.yml \
        --neo4j-url bolt://localhost:7687 \
        --neo4j-user neo4j \
        --neo4j-password password
"""

from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, Iterable, List

import yaml
from py2neo import Graph, Node


class LexSupremeLoader:
    """Load knowledge items from YAML and insert them into Neo4j."""

    def __init__(self, yaml_path: str, neo4j_url: str, user: str, password: str):
        self.yaml_path = Path(yaml_path)
        self.graph = Graph(neo4j_url, auth=(user, password))

    def load_yaml(self) -> Dict:
        """Read the YAML file into a dictionary."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found at {self.yaml_path}")
        with self.yaml_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def extract_items(self, data: Dict) -> List[Dict]:
        """Flatten the structured YAML sections into item dictionaries."""
        items: List[Dict] = []
        for section, records in data.items():
            for record in records or []:
                items.append(
                    {
                        "id": record.get("id"),
                        "title": record.get("title"),
                        "content": record.get("content"),
                        "category": section,
                        "source": record.get("source"),
                        "url": record.get("url"),
                        "certainty_indices": record.get("certainty_indices", {}),
                        "tags": record.get("tags", []),
                    }
                )
        return items

    def inject_to_neo4j(self, items: Iterable[Dict]) -> None:
        """Insert or merge items into Neo4j as KnowledgeItem nodes."""
        for item in items:
            node = Node(
                "KnowledgeItem",
                id=item.get("id"),
                title=item.get("title"),
                content=item.get("content"),
                category=item.get("category"),
                source=str(item.get("source")),
                url=item.get("url"),
                sharia_certainty=item.get("certainty_indices", {}).get("sharia", 0.0),
                legal_certainty=item.get("certainty_indices", {}).get("legal", 0.0),
                literary_clarity=item.get("certainty_indices", {}).get("literary", 0.0),
                tags=",".join(item.get("tags", [])),
            )
            self.graph.merge(node, "KnowledgeItem", "id")
            print(f"✅ Inserted: {item.get('title')} ({item.get('category')})")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Load Lex Supreme knowledge items into Neo4j")
    parser.add_argument(
        "--yaml-path",
        default="data/lex_supreme_knowledge_base.yml",
        help="Path to the YAML file containing knowledge items",
    )
    parser.add_argument("--neo4j-url", default="bolt://localhost:7687", help="Neo4j bolt URL")
    parser.add_argument("--neo4j-user", default="neo4j", help="Neo4j username")
    parser.add_argument("--neo4j-password", required=True, help="Neo4j password")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()

    loader = LexSupremeLoader(
        yaml_path=args.yaml_path,
        neo4j_url=args.neo4j_url,
        user=args.neo4j_user,
        password=args.neo4j_password,
    )

    data = loader.load_yaml()
    items = loader.extract_items(data)
    loader.inject_to_neo4j(items)


if __name__ == "__main__":
    main()
