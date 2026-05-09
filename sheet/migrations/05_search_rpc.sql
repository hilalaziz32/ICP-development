-- Generic similarity-search RPC reused by all 3 retrieval tools.
-- The caller picks which embedding column to search against
-- ('embedding', 'summary_embedding', or 'label_embedding').
create or replace function search_call_chunks(
  query_embedding   vector(1536),
  embedding_column  text default 'embedding',
  match_client      text default null,
  match_label       text default null,
  match_count       int  default 10
)
returns table (
  id          bigint,
  call_id     bigint,
  client      text,
  start_time  text,
  label       text,
  summary     text,
  text        text,
  similarity  float
)
language plpgsql
as $$
begin
  if embedding_column not in ('embedding','summary_embedding','label_embedding') then
    raise exception 'invalid embedding_column: %', embedding_column;
  end if;

  return query execute format($f$
    select
      c.id, c.call_id, c.client, c.start_time, c.label, c.summary, c.text,
      1 - (c.%I <=> $1) as similarity
    from call_chunks c
    where c.%I is not null
      and ($2::text is null or c.client = $2)
      and ($3::text is null or c.label  = $3)
    order by c.%I <=> $1
    limit $4
  $f$, embedding_column, embedding_column, embedding_column)
  using query_embedding, match_client, match_label, match_count;
end;
$$;
