import os
import re
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# ──────────────────────────────────────────────
# 1. Build table name index from Embeddings dir
# ──────────────────────────────────────────────

# Resolve absolute path to the Embeddings directory
_base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_embeddings_dir = os.path.join(_base_path, os.getenv('DBB_TO_EMBED_PATH', 'src/DBBSchemas/Embeddings'))


def _build_table_index():
    """
    Scans DBBSchemas/Embeddings/ and builds a dict:
        { "dealer": "Dealer", "cliente": "Cliente", ... }
    Keys are lowercased table names; values are the original-cased names.
    """
    index = {}
    if os.path.isdir(_embeddings_dir):
        for filename in os.listdir(_embeddings_dir):
            if filename.endswith('.txt'):
                table_name = filename[:-4]           # strip .txt
                index[table_name.lower()] = table_name
    print(f"📑 Table index loaded: {len(index)} tables")
    return index


TABLE_INDEX = _build_table_index()


# ──────────────────────────────────────────────
# 2. Lexical filter – find matching table names
# ──────────────────────────────────────────────

def find_matching_tables(query: str) -> list[str]:
    """
    Tokenizes the query and checks each token (lowercased)
    against the table name index. Returns a list of
    original-cased table names that match.
    """
    # Extract alphanumeric tokens
    tokens = re.findall(r'[a-záéíóúñü\w]+', query.lower())
    matched = []
    for token in tokens:
        if token in TABLE_INDEX:
            matched.append(TABLE_INDEX[token])
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for name in matched:
        if name not in seen:
            seen.add(name)
            unique.append(name)
    return unique


# ──────────────────────────────────────────────
# 3. Load table document directly from disk
# ──────────────────────────────────────────────

def _load_table_doc(table_name: str):
    """
    Reads the .txt file for the given table name directly
    from the Embeddings directory. Returns a Document or None.
    """
    file_path = os.path.join(_embeddings_dir, f"{table_name}.txt")
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return Document(page_content=content, metadata={"source": file_path})
    return None


# ──────────────────────────────────────────────
# 4. Hybrid search (lexical + semantic)
# ──────────────────────────────────────────────

def hybrid_search(vectorstore, query: str, k: int = 5):
    """
    1. Runs lexical filter to find exact table-name matches.
    2. Loads those documents directly from disk (guaranteed).
    3. Runs standard semantic similarity_search.
    4. Merges: exact matches first, then semantic (deduplicated).
    Returns at most `k` documents.
    """
    matched_tables = find_matching_tables(query)
    print(f"🔤 Lexical matches: {matched_tables}")

    # Load exact-match documents directly from disk
    exact_docs = []
    for table_name in matched_tables:
        doc = _load_table_doc(table_name)
        if doc:
            exact_docs.append(doc)
            print(f"✅ Loaded exact match: {table_name}")
        else:
            print(f"⚠️  File not found for table: {table_name}")

    # Semantic search
    semantic_docs = vectorstore.similarity_search(f"ENTITY: {query}", k=k)

    # Merge: exact matches first, then semantic (deduplicated)
    seen = set()
    final_docs = []

    for doc in exact_docs + semantic_docs:
        # Use the first 120 chars as a dedup key
        content_key = doc.page_content[:120]
        if content_key not in seen:
            seen.add(content_key)
            final_docs.append(doc)

    print(f"📄 Hybrid result: {len(exact_docs)} exact + {len(semantic_docs)} semantic → {len(final_docs)} merged")
    return final_docs[:k]
