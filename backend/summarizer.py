import openai
import time
import logging
import json
from backend.utils import count_tokens
from backend.config import LLM_API_KEY, LLM_MODEL, CACHE_TTL
from backend.evaluator import evaluate_summary_deepeval
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import redis
import os

class SummarizationError(Exception):
    pass


logging.basicConfig(
    filename='backend/logs/summary.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

best_summary_logger = logging.getLogger("best_summary")
best_summary_logger.setLevel(logging.INFO)

best_summary_handler = logging.FileHandler("backend/logs/best_summary.log", mode="w")  # Overwrites for new runs
best_summary_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
best_summary_logger.addHandler(best_summary_handler)


openai.api_key = LLM_API_KEY


ROLE_PROMPTS = {
    "general": "Provide a comprehensive summary",
    "cardiologist": "Focus on cardiac conditions and ECG interpretations.",
    "oncologist": "Highlight cancer-related findings and treatment plans.",
    "nurse": "Provide a simplified summary focusing on patient care needs."
}

if os.getenv("DOCKER_ENV"):  
    redis_url = os.getenv("DOCKER_REDIS_URL", "redis://redis:6379/0")
else: 
    redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0") 
r = redis.Redis.from_url(redis_url)

def get_cached_summary(notes, role):
    key = f"{role}:{hash(notes)}"
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cached_summary(notes, role, summary):
    key = f"{role}:{hash(notes)}"
    r.set(key, json.dumps(summary), ex=86400)  # Cache for 1 day


# Dynamically Decide Whether to Chunk
def process_medical_notes(notes, model_max_tokens=4000):
    """
    Automatically determines if chunking is required based on input token length.
    - If within limits, sends the full note.
    - If too long, applies smart chunking and merges results.
    """
    input_tokens = len(notes.split())  

    if input_tokens <= model_max_tokens:
        logging.info(f"Processing full input without chunking ({input_tokens} tokens).")
        return generate_summary(notes)  

    logging.info(f"Input too long ({input_tokens} tokens). Applying chunking.")

    
    chunks = smart_chunk_text(notes, max_chunk_size=2000)
    chunk_summaries = call_llm_parallel(chunks)
    final_summary = recursive_merge(chunk_summaries)

    return {
        "summary": final_summary,
        "chunks_used": len(chunks),
        "total_tokens": input_tokens,
        "output_tokens": len(final_summary.split())
    }

def estimate_max_tokens(input_text, base_limit=500, max_limit=2000):
    """
    Dynamically estimate max_tokens based on input length.
    
    Args:
        input_text (str): Clinical notes to be summarized.
        base_limit (int): Default minimum limit for small inputs.
        max_limit (int): Upper limit to prevent API failures.
    
    Returns:
        int: Optimized max_tokens value.
    """
    input_length = len(input_text.split())  
    token_estimate = input_length * 1.0
    
    return min(max(base_limit, int(token_estimate)), max_limit)

# Rate-Limiting and Retries for LLM Calls
@retry(
    retry=retry_if_exception_type(openai.APIConnectionError),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    reraise=True
)

def call_llm(prompt, temperature=0.4, num_variants=2):
    """Generate multiple summary variations in a single LLM call."""
    max_tokens = estimate_max_tokens(prompt)
    logging.info("LLM Call: No cache, directly querying API.")

    start_time = time.time()
    response = openai.chat.completions.create(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens,
        n=num_variants
    )
    duration = time.time() - start_time

    output_variants = [
        {
            "summary": choice.message.content.strip(),
            "input_tokens": count_tokens(prompt),
            "output_tokens": count_tokens(choice.message.content.strip()),
            "duration": duration
        }
        for choice in response.choices
    ]

    logging.info(f"Generated {num_variants} summary variations in {duration:.2f}s")

    for i, variant in enumerate(output_variants):
        logging.info(f"Summary {i+1}: {variant['summary']}")

    return output_variants

async def generate_summary(notes, role="general"):

    cached = get_cached_summary(notes, role)
    if cached:
        logging.info("Cache hit: Returning cached summary.")
        return cached

    """Generate multiple summaries and select the best using LLM-based evaluation."""
    role_prompt = ROLE_PROMPTS.get(role.lower(), ROLE_PROMPTS["general"])
    prompt = f"""
    You are a highly-skilled **clinical documentation assistant** specialized in **medical note summarization**. Extract all **medically relevant information** and create a **structured, factual, accurate summary** of the patient's medical history, findings, and treatment course.

    Start with a 2-3 sentence high-level summary mentioning why the patient was admitted, primary condition, major interventions, and final outcome.

    Rules:
	- Start with a 2-3 sentence high-level summary of the case
    - Preserve important medical details exactly.
    - Explicitly state if data is missing: ("No information available").
	- Do NOT add any new information or assumptions.
    - Maintain original dates, conditions, clinical sequences.
    - Include patient details: name, gender, age.
    - Maintain chronological order (admission -> diagnosis -> hospital course -> discharge).

    Summary Structure:

    1. Case Overview
    - Patient Name:
    - Age & Gender:
    - Admission Date:
    - Discharge Date:
    - Primary Reason for Admission:
    - Primary Discharge Diagnoses:
    - Outcome:

    2. Medical History
    - Past Diagnoses:
    - Allergies:
    - Comorbidities:
    - Medications on Admission:
    - Surgical History:

    3. Hospital Course
    - Initial Presentation & Key Symptoms:
    - Vital Signs & Emergency Measures:
    - Major Diagnostic Findings (highlight critical issues):
    - Current Diagnoses:
    - Treatment Plan:
    - Procedures Performed:
    - Medical Management:
    - Complications:
    - Response to Treatment:
    - Important Dates:
    - Attending Physician and Hospital Info:

    4. Discharge Plan
    - Medications on Discharge:
    - Follow-up Recommendations:
    - Final Outcome:

    Clinical Notes to Summarize:
    {notes}
    """

        # Generate multiple summaries in a single call
    summary_variants   = call_llm(prompt, num_variants=2)

    if not isinstance(summary_variants, list):
        logging.error("LLM response was not a list!")
        raise SummarizationError("LLM response was not a list!")

    if not all(isinstance(item, dict) and "summary" in item for item in summary_variants):
        logging.error("Malformed response from LLM!")
        raise SummarizationError("Malformed response from LLM!")
        
    
    evaluation_results = await evaluate_summary_deepeval(notes, summary_variants)

   
    if not isinstance(evaluation_results, list):
        logging.error("Evaluation results not in expected format!")
        raise SummarizationError("Evaluation results not in expected format!")

    best_summary = max(evaluation_results, key=lambda x: x["metrics"]["final score"])
    best_summary_index = best_summary["summary_index"]
    best_summary_content = summary_variants[best_summary_index]

    best_summary_logger.info(f'evaluation: {best_summary["metrics"]}\n{best_summary_content["summary"]}')
    best_summary_handler.flush()

    highlights = [line for line in best_summary_content["summary"].split('\n') if 'critical' in line.lower()]

    result =  {
        "summary": best_summary_content["summary"],
        "highlights": highlights,
        "evaluation": best_summary["metrics"],
        "final_score": best_summary["metrics"]["final score"],
        "input_tokens": best_summary_content["input_tokens"],
        "output_tokens": best_summary_content["output_tokens"],
        "duration": best_summary_content["duration"]
    }

    set_cached_summary(notes, role, result)


    return result 
    