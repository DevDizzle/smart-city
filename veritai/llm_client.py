import os
import json
from typing import Optional, Dict, Any

from google import genai
from google.genai import types

class GeminiClient:
    """Simple wrapper around the official google-genai client."""

    def __init__(self, model_name: str = "gemini-2.5-pro"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")

        # Instantiate a client per the official google-genai guidelines
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_content(self, prompt: str, temperature: float = 0.7,
                         max_output_tokens: Optional[int] = None) -> Optional[str]:
        """
        Generates text content using the configured Gemini model.

        Args:
            prompt: The prompt string to send to the model.
            temperature: Controls the randomness of the output. Lower values
                         mean less random outputs.
            max_output_tokens: The maximum number of tokens to generate.

        Returns:
            The generated text content, or None if an error occurs.
        """
        try:
            config_kwargs: Dict[str, Any] = {"temperature": temperature}
            if max_output_tokens is not None:
                config_kwargs["max_output_tokens"] = max_output_tokens

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(**config_kwargs)
            )
            return response.text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return None

    def generate_structured_content(self, prompt: str, schema: Dict[str, Any],
                                    temperature: float = 0.7) -> Optional[Dict[str, Any]]:
        """
        Generates structured content (JSON) using the configured Gemini model.
        This method instructs the model to return JSON and attempts to parse it.
        For more robust schema enforcement, google-genai's tool_code feature
        would be used, but for this initial implementation, we rely on prompt
        instruction and parsing.

        Args:
            prompt: The prompt string to send to the model.
            schema: A dictionary representing the JSON schema for the desired output.
            temperature: Controls the randomness of the output.

        Returns:
            A dictionary representing the generated structured content, or None if an error occurs.
        """
        # Instruct the model to return JSON and provide the schema as context.
        # The `response_mime_type` is a powerful feature for structured output.
        full_prompt = (
            f"{prompt}\n\n"
            "Please respond in JSON format, adhering to the following schema:\n"
            f"{json.dumps(schema, indent=2)}"
        )

        try:
            config = types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type="application/json",
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config,
            )

            json_content = response.text
            return json.loads(json_content)
        except Exception as e:
            print(f"Error generating structured content with Gemini: {e}")
            return None
