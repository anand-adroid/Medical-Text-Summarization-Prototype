import os
import logging
import pytest
import traceback
from backend.summarizer import generate_summary

LOG_FILE = os.path.join(os.path.dirname(__file__), "summarization_test.log")
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w" 
)
logger = logging.getLogger("summarization_test")



total_tests = 0
failed_tests = 0

def test_summarize_text_files():
    """Test summarization for multiple clinical note files."""

    notes_folder = os.path.join(os.path.dirname(__file__), "../clinical_notes")

    if not os.path.exists(notes_folder):
        logging.error(f"Clinical notes folder not found: {notes_folder}")
        return
    global total_tests, failed_tests

    for file_name in os.listdir(notes_folder):
        if file_name.endswith(".txt"):
            total_tests += 1
            file_path = os.path.join(notes_folder, file_name)

            with open(file_path, "r", encoding="utf-8") as file:
                    notes = file.read().strip()  

            try:
                
                logging.info(f"Processing: {file_name}")
                result = generate_summary(notes, "general")

                assert isinstance(result, dict), f"Invalid response type for `{file_name}`"
                assert "summary" in result, f"No summary generated for `{file_name}`"
                assert len(result["summary"]) > 0, f"Empty summary for `{file_name}`"
                assert result.get("input_tokens", 0) > 0, f"No input tokens for `{file_name}`"
                assert result.get("output_tokens", 0) > 0, f"No output tokens for `{file_name}`"

                logging.info(f"Summary generated for `{file_name}`")
                print(f" Passed: {file_name}")
                print(f"Summary generated for {file_name}")

            except Exception as e:
                failed_tests += 1
                error_message = f"Failed: {file_name}\nError: {str(e)}\nTraceback:\n{traceback.format_exc()}\n"
                logging.error(error_message)
                print(error_message)

    print("\n===========================================")
    print(f"**Final Test Results:**")
    print(f"Passed: {total_tests - failed_tests}")
    print(f"Failed: {failed_tests}")
    print("Check `tests/summarization_test_failures.log` for details on failed tests.")
    print("===========================================\n")


if __name__ == "__main__":
    test_summarize_text_files()
            
