import env
import logging
import os

logger: logging.Logger | None = logging.getLogger('fast-image-viewer')

logger.setLevel(logging.DEBUG if env.DEBUG else logging.INFO)
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
)
