-- Replace search_call_chunks to allow the 3 new embedding columns and to
-- return parent denormalised fields so retrieval is one round-trip.
drop function if exists search_call_chunks(vector, text, text, text, integer);

create or replace function search_call_chunks(
  query_embedding   vector(1536),
  embedding_column  text default 'embedding',
  match_client      text default null,
  match_label       text default null,
  match_count       int  default 10
)
returns table (
  id                bigint,
  call_id           bigint,
  client            text,
  start_time        text,
  label             text,
  label_text        text,
  summary           text,
  text              text,
  parent_pain_point text,
  parent_angle      text,
  parent_specialty  text,
  similarity        float
)
language plpgsql
as $$
begin
  if embedding_column not in (
       'embedding','summary_embedding','label_embedding',
       'pain_point_embedding','angle_embedding','sub_categories_embedding'
  ) then
    raise exception 'invalid embedding_column: %', embedding_column;
  end if;

  return query execute format($f$
    select
      c.id, c.call_id, c.client, c.start_time, c.label, c.label_text, c.summary, c.text,
      c.parent_pain_point, c.parent_angle, c.parent_specialty,
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
