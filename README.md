# Air Passenger Compensation Claim Triage Service

## RAG pipeline

The local retrieval pipeline indexes fixed PDF documents and returns source-grounded passages for `agents.workflow.run_workflow(claim, passages)`. It retrieves document text only; it does not create regulations, eligibility findings, or compensation rules.

### Install

Use Python 3.10 or newer, create and activate a virtual environment, then install:

```powershell
python -m pip install -r requirements.txt
```

The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`. It downloads on first use. Set `RAG_EMBEDDING_MODEL` to another compatible Sentence Transformers model to change it.

### Add fixed documents

Place PDFs in either or both directories:

```text
documents/
  dgca/
    applicable-document.pdf
  airline/
    applicable-document.pdf
```

The loader searches recursively. It extracts text page by page; scanned/image-only PDFs may need OCR before indexing. Source filename and 1-based page number are retained. Section is detected on a best-effort basis from headings such as “Section 2” or “Chapter I”.

### Build or rebuild the index

Run from the repository root after adding or replacing PDFs:

```powershell
python -m rag.retrieval --rebuild
```

This builds `data/rag/faiss.index` and a JSON metadata sidecar. Set `RAG_INDEX_PATH` to change the index location. Run the command again whenever PDFs change. The generated index is local and should not be committed.

### Retrieve and use with agents

```python
from agents.workflow import run_workflow
from rag.retrieval import retrieve_passages

claim = "My flight was delayed ..."
passages = retrieve_passages(claim, top_k=5)
result = run_workflow(claim, passages)
print(result.to_dict())
```

Each returned passage contains `text`, `citation`, `source`, `page`, and `section`. Citation strings include the source filename and page, and the section when available, matching the existing agents' passage contract.

### Tests

Run the basic tests from the repository root:

```powershell
python -m unittest rag.test_rag
```

These test overlap and metadata retention, plus the passage shape accepted by the workflow. They do not download the embedding model or require FAISS at test time.
