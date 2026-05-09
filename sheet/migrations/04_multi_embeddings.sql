-- Add summary + label embeddings alongside the existing chunk-text embedding.
alter table call_chunks
  add column if not exists summary_embedding vector(1536),
  add column if not exists label_embedding   vector(1536);

create index if not exists call_chunks_summary_embedding_hnsw
  on call_chunks using hnsw (summary_embedding vector_cosine_ops);

create index if not exists call_chunks_label_embedding_hnsw
  on call_chunks using hnsw (label_embedding vector_cosine_ops);

-- Reset the embedded flag so the embedder runs again to fill the new columns.
update client_calls set embedded = false where chunked = true;
