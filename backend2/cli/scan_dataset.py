from app.services.dataset import scan_dataset
from log import logger


def main() -> None:
    logger.info('scan_dataset start')
    scan_dataset()
    logger.info('scan_dataset done')


if __name__ == '__main__':
    main()
