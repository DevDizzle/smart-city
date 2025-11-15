import os
import json
import google.generativeai as genai
from typing import Optional, Dict, Any

class GeminiClient:
    """
    A client for interacting with the Google Gemini API using the google-generativeai library.
    """
    def __init__(self, model_name: str = "gemini-2.5-pro"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set.")
        
        # Configure the generative AI library with the API key
        genai.configure(api_key=api_key)
        
        # Initialize the generative model
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={"response_mime_type": "application/json"}
        )
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
            generation_config = {
                "temperature": temperature,
            }
            if max_output_tokens is not None:
                generation_config["max_output_tokens"] = max_output_tokens

            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            # Access the text attribute of the first part of the first candidate
            return response.candidates[0].text
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
        full_prompt = f"{prompt}\n\nPlease respond in JSON format, adhering to the following schema:\n{json.dumps(schema, indent=2)}"
        
        try:
            generation_config = {
                "temperature": temperature,
                "response_mime_type": "application/json", # Instruct model to return JSON
            }
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            # The response.text should directly contain the JSON string due to response_mime_type
            json_content = response.candidates[0].text
            return json.loads(json_content)
        except Exception as e:
            print(f"Error generating structured content with Gemini: {e}")
            return None
