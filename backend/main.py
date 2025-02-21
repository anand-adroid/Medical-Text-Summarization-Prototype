from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import traceback
import time
from loguru import logger
from backend.summarizer import generate_summary
from backend.evaluator import evaluate_summary_deepeval
from backend.feedback import store_feedback
from backend.utils import get_cached_summary, set_cached_summary
from backend.logger import log_request
from backend.summarizer import SummarizationError


app = FastAPI(title="Medical Text Summarization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def cors_json_response(content, status_code=200):
    """Return a JSON response with CORS headers."""
    return JSONResponse(
        content=content,
        status_code=status_code,
        headers={"Access-Control-Allow-Origin": "http://localhost:3000"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions and include CORS headers."""
    traceback.print_exc()
    return cors_json_response(
        {"detail": "Internal Server Error. Check backend logs."}, 
        status_code=500
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle FastAPI HTTP exceptions with CORS headers."""
    return cors_json_response(
        {"detail": exc.detail}, 
        status_code=exc.status_code
    )


# CORS Preflight for `OPTIONS`

@app.options("/{path:path}")
async def preflight_handler(request: Request):
    """Handle CORS preflight requests."""
    return cors_json_response({"message": "Preflight OK"})

# =========================
#  API Models
# =========================
class SummarizeRequest(BaseModel):
    notes: str
    role: str = "general"

class FeedbackRequest(BaseModel):
    request_id: str
    summary: str
    feedback: str

class EvaluationRequest(BaseModel):
    notes: str
    generated_summary: str

# API Routes

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return cors_json_response({"status": "API running"})

@app.post("/summarize")
def summarize(request: SummarizeRequest):
    try:
        """Generate a clinical note summary with caching, evaluation, and logging."""
        start_time = time.time()
        if len(request.notes) < 50:
            return cors_json_response({"detail": "Notes must be at least 50 characters."}, status_code=400)

        cached = get_cached_summary(request.notes, request.role)
        if cached:
            return cors_json_response(cached)

        # Generate Summary
        result = generate_summary(request.notes, request.role)
        end_time = time.time()
        result["response_time"] = round(end_time - start_time, 2)
        log_request(request.notes, result["summary"], result["input_tokens"], result["output_tokens"], result["duration"])

        return cors_json_response(result)
    except SummarizationError as e:
        logging.error(f"Summarization failed: {e}")
        return cors_json_response({"detail": str(e)}, status_code=500)

@app.get("/feedback")
def get_feedback():
    """Retrieve recent feedback entries."""
    feedback_path = "backend/logs/feedback.json"
    try:
        with open(feedback_path, "r") as feedback_file:
            feedback_lines = feedback_file.readlines()[-50:]
        feedback_entries = [json.loads(line) for line in feedback_lines]
        return cors_json_response({"feedback": feedback_entries})
    except Exception:
        return cors_json_response({"detail": "No feedback available."}, status_code=500)

@app.post("/feedback")
def submit_feedback(request: FeedbackRequest):
    """Submit clinician feedback for model improvement."""
    response = store_feedback(request.request_id, request.summary, request.feedback)
    return cors_json_response(response)

@app.post("/evaluate")
def evaluate_summary_endpoint(request: EvaluationRequest):
    """Evaluate the generated summary for quality."""
    evaluation = evaluate_summary_deepeval(request.notes, request.generated_summary)
    return cors_json_response({"evaluation": evaluation})

@app.get("/logs")
def get_logs():
    """Return the last 50 log lines for debugging."""
    log_path = "backend/logs/summary.log"
    try:
        with open(log_path, "r") as log_file:
            log_lines = log_file.readlines()[-50:]
        return cors_json_response({"logs": "".join(log_lines)})
    except Exception:
        return cors_json_response({"detail": "No logs available."}, status_code=500)

def close_logs():
    logger.info("Shutting down... Closing log files.")
    time.sleep(1)  
    for handler in logger._core.handlers:
        try:
            handler._sink._file.close()
        except Exception:
            pass

@app.on_event("shutdown")
def shutdown_event():
    close_logs()
