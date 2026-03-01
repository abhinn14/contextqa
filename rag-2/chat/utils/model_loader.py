import os
import sys
import json
from dotenv import load_dotenv
from chat.utils.config_loader import load_config
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from chat.logger import GLOBAL_LOGGER as log
from chat.exception.exception_handler import DocumentPortalException

class ApiKeyManager:
    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("apikeyliveclass")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                log.warning("Failed to parse API_KEYS as JSON", error=str(e))




        # Load API keys for different providers
        for key in ["GROQ_API_KEY", "VLLM_API_KEY"]:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    log.info(f"Loaded {key} from individual env var")

        if self.api_keys:
            log.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})
        else:
            log.info("No API keys configured")


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val


class ModelLoader:
    """
    Loads embedding models and LLMs based on config and environment.
    """

    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))


    def load_embeddings(self):
        """Load and return embedding model based on config provider."""
        try:
            emb_cfg = self.config["embedding_model"]
            provider = emb_cfg.get("provider", "huggingface")
            model_name = emb_cfg.get("model_name")
            log.info("Loading embedding model", provider=provider, model=model_name)
            if provider == "huggingface":
                return HuggingFaceEmbeddings(model_name=model_name)

            raise ValueError(f"Unsupported embedding provider: {provider}. Use 'huggingface'.")

        except Exception as e:
            log.error("Error loading embedding model", error=str(e))
            raise DocumentPortalException("Failed to load embedding model", sys)

    def load_llm(self):
        """
        Load and return the configured LLM model.
        Supports both Groq (for local dev) and vLLM (for RunPod production).
        Set LLM_PROVIDER env var to switch: "groq" or "vllm"
        """
        llm_block = self.config["llm"]
        
        # Get provider from env var, default to "groq" for local development
        provider_key = os.getenv("LLM_PROVIDER", "groq").lower()
        
        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider=provider_key)
            raise ValueError(f"LLM provider '{provider_key}' not found in config. Use 'groq' or 'vllm'.")

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loading LLM", provider=provider, model=model_name)

        if provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=self.api_key_mgr.get("GROQ_API_KEY"),
                temperature=temperature,
            )

        if provider == "vllm":
            # vLLM serves OpenAI-compatible API, use ChatOpenAI with custom base_url
            # Allow base_url override via env var for flexibility
            base_url = os.getenv("VLLM_BASE_URL", llm_config.get("base_url", "http://localhost:8000/v1"))
            # Ensure base_url ends with /v1 for OpenAI-compatible API
            if not base_url.rstrip("/").endswith("/v1"):
                base_url = base_url.rstrip("/") + "/v1"
            api_key = self.api_key_mgr.api_keys.get("VLLM_API_KEY", "EMPTY")
            log.info("Using vLLM endpoint", base_url=base_url)
            return ChatOpenAI(
                model=model_name,
                base_url=base_url,
                api_key=api_key,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        log.error("Unsupported LLM provider", provider=provider)
        raise ValueError(f"Unsupported LLM provider: {provider}. Use 'groq' or 'vllm'.")


if __name__ == "__main__":
    loader = ModelLoader()

    # Test Embedding
    embeddings = loader.load_embeddings()
    print(f"Embedding Model Loaded: {embeddings}")
    result = embeddings.embed_query("Hello, how are you?")
    print(f"Embedding Result: {result}")

    # Test LLM
    llm = loader.load_llm()
    print(f"LLM Loaded: {llm}")
    result = llm.invoke("Hello, how are you?")
    print(f"LLM Result: {result.content}")