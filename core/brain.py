import urllib.request
import json
from config import REGION, MODEL_ID, AWS_ACCESS_KEY, MAX_TOKENS, TEMPERATURE

class Brain:
    def __init__(self, model_id: str = MODEL_ID, region: str = REGION,
                 api_key: str = AWS_ACCESS_KEY):
        self.model_id = model_id
        self.region = region
        # The single custom API key (the Base64 string)
        self.api_key = api_key
        # We construct the URL exactly as the Dart app does
        self.url = self._build_url()

    def _build_url(self) -> str:
        return f"https://bedrock-runtime.{self.region}.amazonaws.com/model/{self.model_id}/converse"

    def reconfigure(self, model_id: str = None, region: str = None, api_key: str = None) -> None:
        """Hot-swap model/region/key at runtime and rebuild the endpoint URL."""
        if model_id:
            self.model_id = model_id
        if region:
            self.region = region
        if api_key:
            self.api_key = api_key
        self.url = self._build_url()

    def think(self, messages: list, system: str = "") -> str:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key
        }
        
        bedrock_messages = []
        for msg in messages:
            bedrock_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        body = {
            "messages": bedrock_messages,
            "inferenceConfig": {
                "maxTokens": MAX_TOKENS,
                "temperature": TEMPERATURE
            }
        }
        
        if system:
            body["system"] = [{"text": system}]

        req = urllib.request.Request(
            self.url, 
            data=json.dumps(body).encode("utf-8"), 
            headers=headers, 
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result["output"]["message"]["content"][0]["text"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise Exception(f"API Error {e.code}: {error_body}")

    def converse(self, messages: list, system: str = "", tool_config: dict = None,
                 temperature: float = 0.2) -> tuple:
        """Native tool-use call. Returns (message_dict, stop_reason, usage).

        `message_dict` is the full assistant message (its `content` is a list of
        blocks that may include `text` and/or `toolUse`). `usage` is the Bedrock
        token-usage dict ({inputTokens, outputTokens, totalTokens}) or {}.
        `tool_config` is passed straight through as the Converse `toolConfig`.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "x-api-key": self.api_key
        }

        bedrock_messages = []
        for msg in messages:
            bedrock_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        body = {
            "messages": bedrock_messages,
            "inferenceConfig": {
                "maxTokens": MAX_TOKENS,
                "temperature": temperature
            }
        }

        if system:
            body["system"] = [{"text": system}]
        if tool_config:
            body["toolConfig"] = tool_config

        req = urllib.request.Request(
            self.url,
            data=json.dumps(body).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return (
                    result["output"]["message"],
                    result.get("stopReason"),
                    result.get("usage") or {},
                )
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise Exception(f"API Error {e.code}: {error_body}")
