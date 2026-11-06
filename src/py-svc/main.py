"""Development entry point for py-svc."""

import logging
import multiprocessing
import sys

import uvicorn

from app.config import ConfigError, Settings
from app.lifecycle import create_app


def main() -> int:
    try:
        settings = Settings.from_env()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr, flush=True)
        return 2

    app = create_app(settings)
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host="127.0.0.1",
            port=settings.port,
            reload=False,
            log_level="info",
            log_config=None,
        )
    )
    app.state.server = server
    server.run()
    return 0


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
