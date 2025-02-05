from .openai_backend import OpenAIBackend

class TogetherBackend(OpenAIBackend):
    """
    Backend for Together.ai

    Uses the OpenAI client, so should be models that support it along with OpenAI function calling:
    https://docs.together.ai/docs/function-calling
    """
    NAME = "together"
    MODELS = {
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo": {
            "max_context": 131072,
            "cost_per_input_token": 0.18e-06,
            "cost_per_output_token": 0.18e-06,
        },
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo": {
            "max_context": 131072,
            "cost_per_input_token": 0.88e-06,
            "cost_per_output_token": 0.88e-06,
        },
        "meta-llama/Llama-3.3-70B-Instruct-Turbo": {
            "max_context": 131072,
            "cost_per_input_token": 0.88e-06,
            "cost_per_output_token": 0.88e-06,
        },
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo": {
            "max_context": 130815,
            "cost_per_input_token": 3.5e-06,
            "cost_per_output_token": 3.5e-06,
        }
    }

    def __init__(self, role, model, tools, api_key, config):
        super().__init__(role, model, tools, api_key, config)
        # Reset the client base URL
        self.client.base_url = "https://api.together.xyz/v1"
