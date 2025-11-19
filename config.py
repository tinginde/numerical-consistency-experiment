"""
Configuration file for numerical consistency experiment.
"""
import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
VIZ_DIR = PROJECT_ROOT / "visualizations"
RESPONSES_DIR = DATA_DIR / "responses"

# Ensure directories exist
for dir_path in [DATA_DIR, RESULTS_DIR, VIZ_DIR, RESPONSES_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Configuration
# Note: API key should be set as environment variable ANTHROPIC_API_KEY
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_NAME = "claude-sonnet-4-5-20250929"  # Claude Sonnet 4.5

# Experiment Configuration
NUM_QUESTIONS_PER_CATEGORY = 25  # For full experiment
NUM_TEST_QUESTIONS = 10  # For initial testing
NUM_REPETITIONS = 3  # Number of times to repeat each question
TEMPERATURE = 0.0  # For consistency

# Question Categories
CATEGORIES = {
    "arithmetic": "基本算術",
    "percentage": "百分比與比例",
    "conversion": "單位轉換",
    "comparison": "比較與排序"
}

# Paraphrase types
PARAPHRASE_TYPES = ["direct", "contextualized", "variation"]

# File paths
QUESTIONS_FILE = DATA_DIR / "questions.json"
GROUND_TRUTH_FILE = DATA_DIR / "ground_truth.json"
CLAUDE_RESPONSES_FILE = RESPONSES_DIR / "claude_responses.json"
ACCURACY_RESULTS_FILE = RESULTS_DIR / "accuracy_results.csv"
CONSISTENCY_RESULTS_FILE = RESULTS_DIR / "consistency_results.csv"
ERROR_ANALYSIS_FILE = RESULTS_DIR / "error_analysis.csv"
