import logging
from rich.console import Console
from rich.logging import RichHandler

console = Console()

def setup_logger(level="INFO"):
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, console=console)]
    )
    log = logging.getLogger("wifi_agent")
    return log

log = setup_logger()
