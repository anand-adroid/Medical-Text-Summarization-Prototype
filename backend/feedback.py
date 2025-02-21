import json
import os
from datetime import datetime
from loguru import logger

FEEDBACK_FILE = "backend/logs/feedback.json"

def store_feedback(request_id, summary, feedback):
    """Store clinician feedback for model improvement."""
    feedback_entry = {
        "request_id": request_id,
        "summary": summary,
        "feedback": feedback,
        "timestamp": datetime.now().isoformat()
    }

    os.makedirs(os.path.dirname(FEEDBACK_FILE), exist_ok=True)

    with open(FEEDBACK_FILE, "a") as file:
        json.dump(feedback_entry, file)
        file.write("\n")

    logger.info(f"Feedback received for Request ID: {request_id}")

    return {"status": "Feedback recorded successfully"}
