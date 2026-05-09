-- Run in Supabase SQL editor.
create extension if not exists vector;

create table if not exists call_chunks (
  id           bigserial primary key,
  call_id      bigint not null references client_calls(id) on delete cascade,
  client       text   not null,
  chunk_idx    int    not null,
  start_time   text,                 -- e.g. "12:34" or "01:02:03"
  end_time     text,
  speakers     text[] default '{}',  -- speakers in this chunk
  text         text   not null,      -- verbatim dialogue, multi-line
  label        text,                 -- pain | ideal_outcome | current_solution
                                     -- | tried_failed | belief | objection | context
  summary      text,                 -- one-line gist of the chunk
  embedding    vector(1536),         -- Gemini gemini-embedding-001 truncated to 1536
  created_at   timestamptz default now(),
  unique (call_id, chunk_idx)
);

create index if not exists call_chunks_call_id_idx on call_chunks (call_id);
create index if not exists call_chunks_client_idx  on call_chunks (client);
create index if not exists call_chunks_label_idx   on call_chunks (label);
-- HNSW for fast cosine ANN. Build after embeddings are populated for best recall.
create index if not exists call_chunks_embedding_hnsw
  on call_chunks using hnsw (embedding vector_cosine_ops);
