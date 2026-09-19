# warden_logger.py
import logging

logging.basicConfig(
    filename="warden_deviations.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

class StateAdmissionException(Exception):
    pass

def screen_stage(stage_id: int, deviation: float, tolerance: float = 0.005):
    if abs(deviation) > tolerance:
        msg = f"Stage {stage_id} OUT OF BOUNDS: dev={deviation:+.4f}, limit=±{tolerance}"
        logging.error(msg)
        raise StateAdmissionException(msg)
    logging.info(f"Stage {stage_id} ADMITTED: dev={deviation:+.4f} within limit ±{tolerance}")
    return True
