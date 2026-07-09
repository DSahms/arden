import traceback
import os
import sys

# Ensure project root is on sys.path so `modules` package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    try:
        from modules.memory_vault import ChromaStore, MemoryManager, embed_text
    except Exception:
        # embed_text may fail if sentence-transformers / torch can't be loaded;
        # we'll fall back to a deterministic mock embedding below for the smoke test.
        from modules.memory_vault import ChromaStore, MemoryManager
    print('Imported memory_vault components')

    # Use a lightweight deterministic mock embedding to avoid heavy deps (torch)
    import hashlib, random

    def mock_embedding(text: str):
        seed = int(hashlib.sha256(text.encode('utf-8')).hexdigest()[:16], 16)
        rnd = random.Random(seed)
        return [rnd.random() for _ in range(384)]

    # For a smoke test, always use the lightweight mock embedding to avoid
    # heavy runtime deps (torch) on Windows CI/local dev environments.
    chroma = ChromaStore(persist_directory=None, embedding_function=mock_embedding)
    print('ChromaStore initialized')

    mm = MemoryManager(neo4j_client=None, chroma_store=chroma, embedding_function=mock_embedding)
    print('MemoryManager initialized')

    print('-> calling remember()')
    try:
        mid = mm.remember('Unit test: remember this sentence about Python.', memory_type='fact', importance=0.8, entity_names=['Python'])
        print('-> remember() returned:', mid)
    except Exception:
        print('-> remember() raised:')
        traceback.print_exc()

    print('-> calling recall()')
    try:
        results = mm.recall('Tell me about Python', limit=3)
        print('-> recall() returned count:', len(results))
        for r in results:
            print(' ->', r.get('content'))
    except Exception:
        print('-> recall() raised:')
        traceback.print_exc()

except Exception as e:
    print('ERROR during smoke test:')
    traceback.print_exc()
    raise
