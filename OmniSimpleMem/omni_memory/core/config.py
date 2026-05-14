"""
Configuration classes for Omni-Memory system.

Provides comprehensive configuration for all components of the Omni-Memory
system including embedding, storage, retrieval, LLM, events, and entropy triggers.
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any


@dataclass
class EmbeddingConfig:
    """Configuration for embedding models."""

    model_name: str = "all-MiniLM-L6-v2"
    embedding_dim: int = 384
    visual_embedding_model: str = "UCSC-VLAA/openvision-vit-large-patch14-224"
    visual_embedding_dim: int = 768
    batch_size: int = 32
    max_seq_length: int = 512
    normalize_embeddings: bool = True


@dataclass
class RetrievalConfig:
    """Configuration for retrieval strategies."""

    default_top_k: int = 10
    enable_hybrid_search: bool = True
    enable_graph_traversal: bool = True
    semantic_weight: float = 0.7
    bm25_weight: float = 0.3
    graph_weight: float = 0.0
    max_expansion_depth: int = 3
    expansion_threshold: float = 0.8


@dataclass
class StorageConfig:
    """Configuration for storage backends."""

    base_dir: str = "./omni_memory_data"
    cold_storage_dir: str = "./omni_memory_data/cold_storage"
    index_dir: str = "./omni_memory_data/index"
    use_s3: bool = False
    s3_bucket: Optional[str] = None
    s3_region: str = "us-east-1"
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    compression_enabled: bool = True
    max_file_size_mb: int = 100


@dataclass
class LLMConfig:
    """Configuration for LLM services."""

    summary_model: str = "gpt-4o-mini"
    query_model: str = "gpt-4o-mini"
    caption_model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 1000
    api_key: Optional[str] = None
    api_base_url: Optional[str] = None
    timeout_seconds: int = 30

    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_base_url is None:
            self.api_base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")


@dataclass
class EventConfig:
    """Configuration for event management."""

    auto_create_events: bool = True
    event_time_window_seconds: float = 300.0  # 5 minutes
    max_events_per_session: int = 100
    min_event_duration_seconds: float = 10.0
    event_summary_max_length: int = 200
    enable_event_hierarchy: bool = True
    max_hierarchy_depth: int = 3
    summarize_on_close: bool = True
    max_maus_for_summary: int = 10


@dataclass
class EntropyTriggerConfig:
    """Configuration for entropy-based triggering."""

    visual_similarity_threshold_high: float = 0.9
    visual_similarity_threshold_low: float = 0.3
    audio_similarity_threshold_high: float = 0.85
    audio_similarity_threshold_low: float = 0.4
    text_entropy_threshold: float = 0.7
    enable_visual_trigger: bool = True
    enable_audio_trigger: bool = True
    enable_text_trigger: bool = True
    trigger_cooldown_seconds: float = 1.0
    # Visual encoder settings
    visual_encoder: str = "clip"
    visual_model_name: Optional[str] = None
    # Audio VAD settings
    audio_energy_threshold: float = 0.01
    audio_vad_threshold: float = 0.5
    audio_min_speech_duration_ms: int = 500


@dataclass
class EvolutionConfig:
    """Configuration for self-evolution capabilities."""

    enable_strategy_optimization: bool = True
    enable_experience_engine: bool = True
    evolution_interval_hours: int = 24
    max_evolution_steps: int = 10
    evolution_temperature: float = 0.1
    preserve_core_functionality: bool = True


@dataclass
class OmniMemoryConfig:
    """
    Main configuration class for Omni-Memory system.

    Provides unified configuration for all components with sensible defaults.
    """

    # Sub-configurations
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    retrieval: RetrievalConfig = field(default_factory=RetrievalConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    llm: LLMConfig = field(default_factory=LLMConfig)
    event: EventConfig = field(default_factory=EventConfig)
    entropy_trigger: EntropyTriggerConfig = field(default_factory=EntropyTriggerConfig)
    evolution: Optional[EvolutionConfig] = None

    # Global settings
    debug_mode: bool = False
    log_level: str = "INFO"
    enable_self_evolution: bool = False

    @classmethod
    def create_default(cls) -> "OmniMemoryConfig":
        """Create a default configuration with sensible defaults."""
        return cls()

    def set_unified_model(self, model_name: str) -> "OmniMemoryConfig":
        """Set the same model for all LLM operations."""
        self.llm.summary_model = model_name
        self.llm.query_model = model_name
        self.llm.caption_model = model_name
        return self

    def enable_evolution(self) -> "OmniMemoryConfig":
        """Enable self-evolution capabilities."""
        self.enable_self_evolution = True
        if self.evolution is None:
            self.evolution = EvolutionConfig()
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = asdict(self)
        # Convert None values to empty dicts for optional configs
        if self.evolution is None:
            result["evolution"] = {}
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OmniMemoryConfig":
        """Create configuration from dictionary."""
        # Handle optional evolution config
        evolution_data = data.pop("evolution", None)
        if evolution_data:
            data["evolution"] = EvolutionConfig(**evolution_data)

        _class_map = {
            "embedding": EmbeddingConfig,
            "retrieval": RetrievalConfig,
            "storage": StorageConfig,
            "llm": LLMConfig,
            "event": EventConfig,
            "entropy_trigger": EntropyTriggerConfig,
        }
        for key, config_class in _class_map.items():
            if key in data and isinstance(data[key], dict):
                data[key] = config_class(**data[key])

        return cls(**data)

    def to_json(self) -> str:
        """Serialize configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "OmniMemoryConfig":
        """Create configuration from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def ensure_directories(self) -> None:
        """Create required storage directories if they don't exist."""
        import pathlib
        for d in [self.storage.base_dir, self.storage.cold_storage_dir, self.storage.index_dir]:
            pathlib.Path(d).mkdir(parents=True, exist_ok=True)

    def save_to_file(self, filepath: str) -> None:
        """Save configuration to a JSON file."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.to_json())

    @classmethod
    def from_file(cls, filepath: str) -> "OmniMemoryConfig":
        """Load configuration from a JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return cls.from_json(f.read())