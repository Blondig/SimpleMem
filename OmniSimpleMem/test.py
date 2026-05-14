from omni_memory import OmniMemoryOrchestrator, OmniMemoryConfig

config = OmniMemoryConfig()
config.embedding.model_name = "all-MiniLM-L6-v2"
config.embedding.embedding_dim = 384

orchestrator = OmniMemoryOrchestrator(config=config, data_dir="./my_memory")

# Store
orchestrator.add_text(
    "User loves hiking in the Rocky Mountains every summer.",
    tags=["session_id:D1", "timestamp:2024-06-15"],
)

# Query
result = orchestrator.query("What does the user enjoy?", top_k=5)
for item in result.items:
    print(item["summary"])

orchestrator.close()