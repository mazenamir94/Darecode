import os
from dotenv import load_dotenv

load_dotenv()

REGION        = os.getenv("AWS_REGION", "eu-central-1")
MODEL_ID      = os.getenv("BEDROCK_MODEL_ID", "qwen.qwen3-235b-a22b-2507-v1:0")
ENDPOINT      = f"https://bedrock-runtime.{REGION}.amazonaws.com/model/{MODEL_ID}/converse"

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_SESSION    = os.getenv("AWS_SESSION_TOKEN")

MAX_TOKENS    = 8192
TEMPERATURE   = 0.7
