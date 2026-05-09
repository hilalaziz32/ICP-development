-- Knowledge-graph denormalisation: join parent client_calls fields onto every
-- chunk so retrieval can match on pain_point/angle/sub_categories without a
-- runtime JOIN, plus a richer label_text bag-of-words for stronger label search.

alter table call_chunks
  add column if not exists parent_pain_point      text,
  add column if not exists parent_angle           text,
  add column if not exists parent_category        text,
  add column if not exists parent_specialty       text,
  add column if not exists parent_sub_categories  jsonb,
  add column if not exists label_text             text,
  add column if not exists pain_point_embedding     vector(1536),
  add column if not exists angle_embedding          vector(1536),
  add column if not exists sub_categories_embedding vector(1536);

-- Backfill parent columns from client_calls.
update call_chunks ch
   set parent_pain_point     = c.pain_point,
       parent_angle          = c.angle,
       parent_category       = c.category,
       parent_specialty      = c.specialty,
       parent_sub_categories = c.sub_categories
  from client_calls c
 where ch.call_id = c.id;

-- Build label_text = "label | pain_point | summary" for every existing chunk.
-- (Strategic bag-of-words: bucket + the strategic angle the call carries + this
-- chunk's specific gist. This is what gets embedded into label_embedding.)
update call_chunks
   set label_text = trim(both ' |' from
        coalesce(label, 'context') || ' | ' ||
        coalesce(parent_pain_point, '') || ' | ' ||
        coalesce(summary, '')
   );

-- HNSW indexes for the new embedding columns.
create index if not exists call_chunks_pain_emb_hnsw
  on call_chunks using hnsw (pain_point_embedding vector_cosine_ops);
create index if not exists call_chunks_angle_emb_hnsw
  on call_chunks using hnsw (angle_embedding vector_cosine_ops);
create index if not exists call_chunks_subcats_emb_hnsw
  on call_chunks using hnsw (sub_categories_embedding vector_cosine_ops);

-- Drop the old label_embedding (was just embedding the bare label word) so the
-- embedder regenerates it from the new label_text.
update call_chunks set label_embedding = null;

-- Reset embedded flag so the embedder fills the 3 new columns + new label_text.
update client_calls set embedded = false where chunked = true;
