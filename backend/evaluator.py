from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from deepeval.metrics import SummarizationMetric, GEval
from deepeval import evaluate
import spacy
import nltk
import numpy as np
from scipy.spatial.distance import cosine
from backend.config import LLM_MODEL, LLM_API_KEY
from langchain_openai import OpenAIEmbeddings
import openai
import asyncio
import sys
from loguru import logger

logger.add("backend/logs/evaluator.log", rotation="1 MB", level="INFO", format="{time} | {level} | {message}")


nlp = spacy.load("en_core_web_sm")

openai_client = openai.OpenAI(api_key=LLM_API_KEY)

# To capture important clinical terms
def get_medical_entity_density(text):
    tokens = nltk.word_tokenize(text)
    num_tokens = len(tokens)
    doc = nlp(text)
    num_entities = len(doc.ents)
    return num_entities / max(num_tokens, 1)

# To detect sentence disconnects
def compute_coherence_score(summary):
    sentences = summary.split('.')
    if len(sentences) < 2:
        return 0

    embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
    sentence_embeddings = embedding_model.embed_documents(sentences)

    similarities = []
    for i in range(len(sentence_embeddings) - 2):
        emb1 = np.array(sentence_embeddings[i])
        emb2 = np.array(sentence_embeddings[i + 2])
        similarity = 1 - cosine(emb1, emb2)
        similarities.append(similarity)

    return np.mean(similarities) if similarities else 0


medical_redundancy_metric = GEval(
    name="Medical Repetitiveness",
    criteria="Avoid repeating symptoms, conditions, or treatments unnecessarily.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],  # FIXED
    verbose_mode=True
)

medical_vagueness_metric = GEval(
    name="Medical Vagueness",
    criteria="Avoid vague descriptions and ensure specificity.",
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT], 
    verbose_mode=True
)

#def is_uvloop():
#    return isinstance(asyncio.get_event_loop(), asyncio.AbstractEventLoop) and 'uvloop' in sys.modules

async def generate_truths(prompt):
    try:
        response = await openai_client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role":"user", "content":prompt}],
            temperature=0.4
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API Error: {e}")
        return "Error generating truths."


# DeepEval-Based Evaluation
async def evaluate_summary_deepeval(input_notes, summaries):
    logger.info("Starting evaluation of summaries...")

    if isinstance(summaries, dict):  
        summaries = [summaries]  

    if not isinstance(summaries, list):
        logger.error("ERROR: `summaries` is not a list! It is:", type(summaries))
        return {"error": "Evaluation failed: summaries must be a list of dictionaries."}

    if not all(isinstance(s, dict) and "summary" in s for s in summaries):
        logger.error("ERROR: Summaries do not contain 'summary' keys! Received:", summaries)
        return {"error": "Evaluation failed: Each item must be a dictionary with 'summary' key."}

    test_cases = [LLMTestCase(input=input_notes, actual_output=s["summary"]) for s in summaries]

    summarization_metric = SummarizationMetric(
        verbose_mode=True,
        n=20,
        truths_extraction_limit=50
    )

    try:
        eval_results = evaluate(
            test_cases,
            [summarization_metric, medical_redundancy_metric, medical_vagueness_metric]
        )
    except AttributeError as e:
        logger.error(f"DeepEval Error: {e}. Using manual truth generation.")
        truth_data = await generate_truths(input_notes)
        summarization_metric.truths = [truth_data]
        eval_results = evaluate(
            test_cases,
            [summarization_metric, medical_redundancy_metric, medical_vagueness_metric]
        )

    formatted_results = []

    for i, result in enumerate(eval_results.test_results):  
        try:
            metrics_data = result.metrics_data 
        except AttributeError:
            logger.error(f"ERROR: Test result does not contain expected `metrics_data` field: {result}")
            continue 

        summarization_score = metrics_data[0].score  # Measures alignment & factual accuracy to prevent hallucinations
        redundancy_score = metrics_data[1].score  # To improve summary efficiency
        vagueness_score = metrics_data[2].score  # To ensure medical clarity

        
        coherence_score = compute_coherence_score(summaries[i]["summary"])
        entity_density_score = get_medical_entity_density(summaries[i]["summary"])

        
        alignment_score = summarization_score  
        coverage_score = summarization_score  
        final_score = (2 * alignment_score * coverage_score) / (alignment_score + coverage_score) if alignment_score + coverage_score > 0 else 0

        formatted_results.append({
            "summary_index": i,
            "metrics": {
                "Summarization Score": summarization_score,
                "Alignment Score": alignment_score,
                "Coverage Score": coverage_score,
                "Entity Density Score": entity_density_score,
                "Coherence Score": coherence_score,
                "Vagueness Score": vagueness_score,
                "Repetitiveness Score": redundancy_score,
                "final score":final_score
            },
            "feedback": result.feedback if hasattr(result, 'feedback') else "Evaluation completed.",
            "summary": summaries[i]["summary"]
        })
        logger.info(f"Evaluation Metrics for summary {i}: {formatted_results[-1]['metrics']}")
    logger.success("Evaluation completed successfully!")

    return formatted_results