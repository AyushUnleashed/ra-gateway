from rich.logging import RichHandler
import logging


# Configure the logger to use RichHandler with detailed format including timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt="[%Y-%m-%d %H:%M:%S]",
    handlers=[RichHandler()]
)

logger = logging.getLogger("rich")
