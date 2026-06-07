"""
GROOVE.AI - Shared Configuration Loader
All modules use this library to read from config.yaml
"""

import yaml
from pathlib import Path
from typing import Any, Dict, Optional
import os


class ConfigLoader:
    """
    Centralized configuration loader.
    All modules use this to access configuration.
    """
    
    _instance = None
    _config: Dict[str, Any] = {}
    _config_path: str = "config.yaml"
    
    def __new__(cls):
        """Singleton pattern - only one instance."""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from YAML file."""
        # Try to find config.yaml in multiple locations
        possible_paths = [
            Path(self._config_path),  # Current directory
            Path(__file__).parent.parent / self._config_path,  # Project root
            Path.cwd() / self._config_path,  # Working directory
        ]
        
        config_file = None
        for path in possible_paths:
            if path.exists():
                config_file = path
                break
        
        if not config_file:
            raise FileNotFoundError(
                f"config.yaml not found in any of: {[str(p) for p in possible_paths]}"
            )
        
        with open(config_file, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
        
        print(f"[OK] Configuration loaded from: {config_file}")
    
    def reload(self):
        """Reload configuration from file."""
        self._load_config()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path (e.g., "database.modules.orchestrator")
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Examples:
            >>> config = ConfigLoader()
            >>> config.get("global.project_name")
            'GROOVE.AI'
            >>> config.get("network.orchestrator.port")
            8100
        """
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire configuration dictionary."""
        return self._config.copy()
    
    # =============================================================================
    # CONVENIENCE GETTERS - Commonly used configurations
    # =============================================================================
    
    # Global Settings
    def get_project_name(self) -> str:
        """Get project name."""
        return self.get("global.project_name", "GROOVE.AI")
    
    def get_version(self) -> str:
        """Get project version."""
        return self.get("global.version", "2.0.0")
    
    def get_environment(self) -> str:
        """Get environment (development, staging, production)."""
        return self.get("global.environment", "development")
    
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.get("global.debug", False)
    
    def get_log_level(self) -> str:
        """Get log level."""
        return self.get("global.log_level", "INFO")
    
    # Development Settings
    def get_sample_file(self) -> str:
        """Get sample file path for development."""
        return self.get("development.sample_file", "DOCUMENTS/DEV/sample.pdf")
    
    def get_test_data_dir(self) -> str:
        """Get test data directory."""
        return self.get("development.test_data_dir", "DOCUMENTS/DEV")
    
    # Database
    def get_database_url(self, module_name: str) -> str:
        """
        Get database URL for specific module.
        
        Args:
            module_name: Name of the module (e.g., "orchestrator", "file_reader")
        
        Returns:
            Database URL
        """
        return self.get(f"database.modules.{module_name}", 
                       f"sqlite:///data/databases/{module_name}.db")
    
    def get_master_database_url(self) -> str:
        """Get master database URL."""
        return self.get("database.master_url", "sqlite:///data/databases/grooveai_master.db")
    
    # Network
    def get_module_host(self, module_name: str) -> str:
        """Get host for specific module."""
        return self.get(f"network.modules.{module_name}.host", "0.0.0.0")
    
    def get_module_port(self, module_name: str) -> int:
        """Get port for specific module."""
        default_ports = {
            "file_reader": 8101,
            "text_normalizer": 8102,
            "latinizer": 8103,
            "embedding_generator": 8104,
            "legal_parser": 8105,
            "legal_unit_extractor": 8105,
            "assertion_extractor": 8106,
            "entity_recognizer": 8107,
            "condition_extractor": 8108,
            "assertion_classifier": 8109,
            "vector_store": 8111,
            "keyword_indexer": 8112,
            "hybrid_search": 8113,
            "ontology_matcher": 8114,
            "reference_resolver": 8115,
            "definition_extractor": 8116,
            "candidate_finder": 8117,
            "conflict_detector": 8118,
            "severity_calculator": 8119,
            "recommendation_generator": 8120,
        }
        return self.get(f"network.modules.{module_name}.port", 
                       default_ports.get(module_name, 8100))
    
    def get_module_url(self, module_name: str) -> str:
        """Get full URL for specific module."""
        return self.get(f"network.modules.{module_name}.url", 
                       f"http://localhost:{self.get_module_port(module_name)}")
    
    def get_orchestrator_host(self) -> str:
        """Get orchestrator host."""
        return self.get("network.orchestrator.host", "0.0.0.0")
    
    def get_orchestrator_port(self) -> int:
        """Get orchestrator port."""
        return self.get("network.orchestrator.port", 8100)
    
    def get_orchestrator_url(self) -> str:
        """Get orchestrator URL."""
        return self.get("network.orchestrator.url", "http://localhost:8100")
    
    # Logging
    def get_log_dir(self) -> str:
        """Get log directory."""
        return self.get("logging.log_dir", "data/logs")
    
    def get_log_file(self, module_name: str) -> str:
        """Get log file path for specific module."""
        return self.get(f"logging.modules.{module_name}", 
                       f"data/logs/{module_name}.log")
    
    def get_log_format(self) -> str:
        """Get log format."""
        return self.get("logging.format", 
                       "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    
    def get_log_date_format(self) -> str:
        """Get log date format."""
        return self.get("logging.date_format", "%Y-%m-%d %H:%M:%S")
    
    # AI Models
    def get_embedding_model(self) -> str:
        """Get embedding model name."""
        return self.get("ai_models.embedding.model_name", "BAAI/bge-m3")
    
    def get_embedding_dimensions(self) -> int:
        """Get embedding dimensions."""
        return self.get("ai_models.embedding.dimensions", 1024)
    
    def get_embedding_device(self) -> str:
        """Get embedding device (cuda/cpu)."""
        return self.get("ai_models.embedding.device", "cuda")
    
    def get_embedding_batch_size(self) -> int:
        """Get embedding batch size."""
        return self.get("ai_models.embedding.batch_size", 32)
    
    def get_ner_language(self) -> str:
        """Get NER language."""
        return self.get("ai_models.ner.language", "sr")
    
    def get_llm_base_url(self) -> str:
        """Get LLM base URL."""
        return self.get("ai_models.llm.base_url", "http://localhost:11434")
    
    def get_llm_model(self) -> str:
        """Get LLM model name."""
        return self.get("ai_models.llm.model", "llama3.2:latest")
    
    def get_llm_temperature(self) -> float:
        """Get LLM temperature."""
        return self.get("ai_models.llm.temperature", 0.7)
    
    # Vector Store
    def get_qdrant_path(self) -> str:
        """Get Qdrant storage path."""
        return self.get("vector_store.path", "data/qdrant_storage")
    
    def get_qdrant_collection(self, collection_type: str) -> str:
        """Get Qdrant collection name."""
        return self.get(f"vector_store.collections.{collection_type}", 
                       f"{collection_type}_assertions")
    
    def get_vector_size(self) -> int:
        """Get vector size."""
        return self.get("vector_store.vector_size", 1024)
    
    # Search
    def get_search_weights(self) -> Dict[str, float]:
        """Get hybrid search weights."""
        return {
            "vector": self.get("search.weights.vector", 0.45),
            "keyword": self.get("search.weights.keyword", 0.35),
            "graph": self.get("search.weights.graph", 0.20),
        }
    
    def get_min_similarity(self) -> float:
        """Get minimum similarity threshold."""
        return self.get("search.min_similarity", 0.25)
    
    # Performance
    def get_batch_size(self, batch_type: str) -> int:
        """Get batch size for specific type."""
        return self.get(f"performance.batch_sizes.{batch_type}", 32)
    
    def get_max_workers(self) -> int:
        """Get max workers for parallel processing."""
        return self.get("performance.max_workers", 4)
    
    def is_cache_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.get("performance.cache.enabled", True)
    
    def get_cache_ttl(self) -> int:
        """Get cache TTL in seconds."""
        return self.get("performance.cache.ttl", 3600)
    
    # File Processing
    def get_supported_formats(self) -> list:
        """Get supported file formats."""
        return self.get("file_processing.supported_formats", ["pdf", "docx", "txt"])
    
    def get_max_file_size(self) -> int:
        """Get max file size in bytes."""
        return self.get("file_processing.max_file_size", 52428800)
    
    def get_file_encoding(self) -> str:
        """Get file encoding."""
        return self.get("file_processing.encoding", "utf-8")
    
    # Directories
    def get_data_dir(self) -> str:
        """Get data directory."""
        return self.get("directories.data", "data")
    
    def get_databases_dir(self) -> str:
        """Get databases directory."""
        return self.get("directories.databases", "data/databases")
    
    def get_logs_dir(self) -> str:
        """Get logs directory."""
        return self.get("directories.logs", "data/logs")
    
    def get_documents_dir(self) -> str:
        """Get documents directory."""
        return self.get("directories.documents", "DOCUMENTS")
    
    # Workflows
    def get_workflow_steps(self, workflow_name: str) -> list:
        """Get workflow steps."""
        return self.get(f"workflows.{workflow_name}.steps", [])
    
    def is_workflow_enabled(self, workflow_name: str) -> bool:
        """Check if workflow is enabled."""
        return self.get(f"workflows.{workflow_name}.enabled", True)
    
    # Features
    def is_feature_enabled(self, feature_name: str) -> bool:
        """Check if feature is enabled."""
        return self.get(f"features.{feature_name}", False)


# =============================================================================
# GLOBAL INSTANCE - Import this in modules
# =============================================================================

config = ConfigLoader()


# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("="*80)
    print("GROOVE.AI Configuration Loader - Examples")
    print("="*80)
    
    # Global settings
    print(f"\nProject Name: {config.get_project_name()}")
    print(f"Version: {config.get_version()}")
    print(f"Environment: {config.get_environment()}")
    print(f"Debug Mode: {config.is_debug()}")
    
    # Development
    print(f"\nSample File: {config.get_sample_file()}")
    print(f"Test Data Dir: {config.get_test_data_dir()}")
    
    # Database
    print(f"\nOrchestrator DB: {config.get_database_url('orchestrator')}")
    print(f"File Reader DB: {config.get_database_url('file_reader')}")
    
    # Network
    print(f"\nOrchestrator URL: {config.get_orchestrator_url()}")
    print(f"File Reader URL: {config.get_module_url('file_reader')}")
    print(f"Legal Parser Port: {config.get_module_port('legal_parser')}")
    
    # Logging
    print(f"\nLog Directory: {config.get_log_dir()}")
    print(f"Orchestrator Log: {config.get_log_file('orchestrator')}")
    
    # AI Models
    print(f"\nEmbedding Model: {config.get_embedding_model()}")
    print(f"Embedding Dimensions: {config.get_embedding_dimensions()}")
    print(f"LLM Model: {config.get_llm_model()}")
    
    # Search
    print(f"\nSearch Weights: {config.get_search_weights()}")
    print(f"Min Similarity: {config.get_min_similarity()}")
    
    # Performance
    print(f"\nEmbedding Batch Size: {config.get_batch_size('embeddings')}")
    print(f"Max Workers: {config.get_max_workers()}")
    print(f"Cache Enabled: {config.is_cache_enabled()}")
    
    # File Processing
    print(f"\nSupported Formats: {config.get_supported_formats()}")
    print(f"Max File Size: {config.get_max_file_size()} bytes")
    
    # Workflows
    print(f"\nImport Corpus Steps: {len(config.get_workflow_steps('import_corpus'))} steps")
    print(f"Analyze Draft Enabled: {config.is_workflow_enabled('analyze_draft')}")
    
    # Using dot notation
    print(f"\nDirect access: {config.get('global.project_name')}")
    print(f"Nested access: {config.get('network.modules.file_reader.port')}")
    
    print("\n" + "="*80)

# Made with Bob
