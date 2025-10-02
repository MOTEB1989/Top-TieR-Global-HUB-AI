import logging
import os
import sys
from typing import Any, Dict

import yaml

from modules.fetchers import handle_fetch
from modules.processors import handle_process
from modules.renderers import handle_render

try:
    from tqdm import tqdm
except Exception:  # pragma: no cover
    def tqdm(iterable, **_: Any):  # type: ignore[misc]
        return iterable


def setup_logger() -> logging.Logger:
    level_name = os.getenv("LEXCODE_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    log_dir = os.getenv("LEXCODE_LOG_DIR", ".")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, os.getenv("LEXCODE_LOG_FILE", "lexcode_runner.log"))

    logger = logging.getLogger("lexcode_runner")
    logger.setLevel(level)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def run_task(logger: logging.Logger, task: Dict[str, Any]) -> None:
    name = task.get("name", "unnamed-task")
    logger.info("➡️ Task: %s", name)

    data: Any = None

    fetch_cfg = task.get("fetch")
    if fetch_cfg:
        try:
            data = handle_fetch(fetch_cfg)
        except Exception as exc:  # pragma: no cover
            logger.exception("Fetch stage failed for %s: %s", name, exc)
            return
    else:
        logger.debug("No fetch config for %s", name)

    process_cfg = task.get("process")
    if process_cfg:
        try:
            data = handle_process(process_cfg, data)
        except Exception as exc:  # pragma: no cover
            logger.exception("Process stage failed for %s: %s", name, exc)
            return
    else:
        logger.debug("No process config for %s", name)

    render_cfg = task.get("render")
    if render_cfg:
        try:
            handle_render(render_cfg, data)
        except Exception as exc:  # pragma: no cover
            logger.exception("Render stage failed for %s: %s", name, exc)
    else:
        logger.debug("No render config for %s", name)


def main() -> None:
    config_path = os.getenv("LEXCODE_CONFIG", "lexcode.yaml")
    if len(sys.argv) > 1:
        config_path = sys.argv[1]

    logger = setup_logger()
    logger.info("🧠 LexCode Runner v1.0")

    if not os.path.exists(config_path):
        logger.error("Configuration file not found: %s", config_path)
        sys.exit(1)

    config = load_config(config_path)
    tasks = config.get("tasks", [])

    if not tasks:
        logger.warning("No tasks defined in %s", config_path)
        return

    for task in tqdm(tasks, desc="LexCode tasks"):
        run_task(logger, task)


if __name__ == "__main__":
    main()
