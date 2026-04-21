"""
Model client - Simple wrapper for vLLM inference.

Usage:
    from client import ModelClient
    client = ModelClient()
    response = client.generate("Hello, how are you?")
"""

import os
from pathlib import Path
from typing import Optional

import yaml


class ModelClient:
    """Client for vLLM model gateway."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize with config."""
        if config_path is None:
            config_path = Path(__file__).parent / "config" / "model-gateway.yaml"

        self.config = self._load_config(config_path)
        self.base_url = self.config["model_gateway"]["base_url"]
        self.api_key = self.config["model_gateway"].get("api_key", "EMPTY")
        self.default_model = self.config["model_gateway"]["default_model"]

    def _load_config(self, config_path: Path) -> dict:
        """Load config from YAML."""
        if not config_path.exists():
            return {"model_gateway": {"base_url": "http://localhost:8080/v1", "api_key": "EMPTY"}}

        with open(config_path) as f:
            return yaml.safe_load(f)

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Generate text from model."""
        import requests

        model = model or self.default_model
        url = f"{self.base_url}/completions"

        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        headers = {}
        if self.api_key and self.api_key != "EMPTY":
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()

        return response.json()["choices"][0]["text"]

    def chat(
        self,
        messages: list[dict],
        model: Optional[str] = None,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> str:
        """Chat completion."""
        import requests

        model = model or self.default_model
        url = f"{self.base_url}/chat/completions"

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        headers = {}
        if self.api_key and self.api_key != "EMPTY":
            headers["Authorization"] = f"Bearer {self.api_key}"

        response = requests.post(url, json=payload, headers=headers, timeout=120)
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]

    def list_models(self) -> list[str]:
        """List available models."""
        import requests

        url = f"{self.base_url}/models"
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        return [m["id"] for m in response.json()["data"]]


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Model client")
    parser.add_argument("--prompt", "-p", help="Prompt for generation")
    parser.add_argument("--chat", "-c", help="Chat message")
    parser.add_argument("--list-models", "-l", action="store_true", help="List models")
    parser.add_argument("--model", "-m", help="Model name")

    args = parser.parse_args()

    client = ModelClient()

    if args.list_models:
        print("Available models:")
        for model in client.list_models():
            print(f"  - {model}")
    elif args.prompt:
        print(client.generate(args.prompt, model=args.model))
    elif args.chat:
        print(client.chat([{"role": "user", "content": args.chat}], model=args.model))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
