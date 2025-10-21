import time

import ecflow as ecf
from loguru import logger

COMPLETE_STATUS = "complete"
ABORTED_STATUS = "aborted"


def await_ecflow_node_to_complete(node_path: str, delay: int = 60) -> None:
    """Await an ecflow node to complete. If the node is aborted, raises an error."""
    ci = ecf.Client()
    status = ""
    while status != COMPLETE_STATUS:
        logger.info(f"Awaiting ecFlow node {node_path} to complete")
        time.sleep(delay)

        try:
            status = ci.query("state", node_path)
        except RuntimeError:
            logger.info("Failed to query ecFlow node, waiting and trying again")
        else:
            # Check for errors
            if status == ABORTED_STATUS:
                logger.error("Suite status is aborted. Exiting with an error.")
                raise RuntimeError("Suite status is aborted")


if __name__ == "__main__":
    await_ecflow_node_to_complete("/test1")
