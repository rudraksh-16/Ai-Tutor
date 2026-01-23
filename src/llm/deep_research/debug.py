import time
import logging
from contextlib import contextmanager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)


@contextmanager
def debug_timer(name: str):
    start = time.time()
    logging.info(f"▶ START: {name}")
    yield
    end = time.time()
    logging.info(f"⏹ END: {name} | took {end - start:.2f}s")
