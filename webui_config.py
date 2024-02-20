from typing import NamedTuple, List, IO, Union
import yaml

# Embedding model configuration.
class EmbeddingModelConfig(NamedTuple):
    provider: str  # Provider of the embedding model i.e. huggingface
    endpoint: str  # Endpoint for the embedding model.

    # Create a new embedding model configuration from a dictionary.
    @classmethod
    def new_embedding_config(cls, config: dict):
        try:
            # Extract provider and endpoint from the config dictionary.
            model_provider = config["provider"].lower()  # Ensure lowercase provider name.
            model_endpoint = config["endpoint"]
        except ValueError as ex:
            raise ValueError("Error while parsing config") from ex
        
        # Return a new instance of EmbeddingModelConfig.
        return cls(provider=model_provider, endpoint=model_endpoint)

# LLM model configuration.
class LlmModelConfig(NamedTuple):
    provider: str  # Provider of the LLM model. i.e. huggingface tgi
    endpoint: str  # Endpoint for the LLM model.
    
    # Create a new LLM model configuration from a dictionary.
    @classmethod
    def new_llm_config(cls, config: dict):
        try:
            # Extract provider and endpoint from the config dictionary.
            model_provider = config["provider"].lower()  # Ensure lowercase provider name.
            model_endpoint = config["endpoint"]
        except ValueError as ex:
            raise ValueError("Error while parsing config") from ex
        
        # Return a new instance of LlmModelConfig.
        return cls(provider=model_provider, endpoint=model_endpoint)
    
# UI configuration
class UiConfig:
    def __init__(self, config: dict):

        # Initialize embedding_model attribute as None.
        self.embedding_model: EmbeddingModelConfig

        # Get embedding model configuration from the input dictionary.
        _embedding_model_config = config.get("embedding_model", None)

        # If embedding model configuration exists, create a new EmbeddingModelConfig instance.
        if _embedding_model_config:
            self.embedding_model = EmbeddingModelConfig.new_embedding_config(_embedding_model_config)
        
        # Initialize llm_models attribute as an empty list.
        self.llm_models: List[LlmModelConfig] = []

        # Get LLM models configurations from the input dictionary.
        _llm_config = config.get("llm_models", [])

        # Loop through each LLM configuration and create LlmModelConfig instances.
        for _llm in _llm_config:
            self.llm_models.append(LlmModelConfig.new_llm_config(_llm))

        self.document_folder: str = config.get("document-folder", "doc")
        
    # Method to load UI configuration from a file
    @classmethod
    def load_config_from_file(cls, config: IO[str]):
        
        # Load YAML configuration from the input file
        _config = yaml.safe_load(config)

        # Return a new instance of UiConfig with loaded configuration
        return cls(_config)
