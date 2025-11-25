"""
Ingestion bridge module - unified wrapper for ingestion operations.
Encapsulates run_ingestion with structured logging and timing.
"""
from typing import Any, Dict, Optional

from app.ingestion.cli import run_ingestion as _original_run_ingestion

from .logging import ingestion_logger, LogTimer


def run_ingestion_with_logging(
    source: str,
    limit: Optional[int] = None,
    index_jsonl: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run ingestion with structured logging and timing.
    
    Args:
        source: Data source name (e.g., "sama")
        limit: Optional limit on number of items to process
        index_jsonl: Optional path to JSONL index file
    
    Returns:
        Dictionary with ingestion results including:
        - source: Source name
        - count: Number of records processed
        - index_path: Path to index file
        - records: List of ingested records
    
    Raises:
        ValueError: If source is not registered
        ImportError: If source dependencies are missing
        Exception: For other ingestion errors
    
    Examples:
        >>> result = run_ingestion_with_logging("sama", limit=10)
        >>> print(f"Ingested {result['count']} records from {result['source']}")
    """
    context = {
        "source": source,
        "limit": limit or "unlimited",
    }
    
    with LogTimer(ingestion_logger, "ingestion", **context):
        result = _original_run_ingestion(source, limit=limit, index_jsonl=index_jsonl)
        
        # Add count to context for success log
        ingestion_logger.info(
            f"Ingested {result['count']} records from {result['source']} "
            f"to {result['index_path']}"
        )
        
        return result


# Alias for backward compatibility
run_ingestion = run_ingestion_with_logging
