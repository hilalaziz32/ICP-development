-- Pipeline-state flags on client_calls. Run in Supabase SQL editor.
alter table client_calls
  add column if not exists chunked  boolean not null default false,
  add column if not exists embedded boolean not null default false;

create index if not exists client_calls_chunked_idx  on client_calls (client, chunked);
create index if not exists client_calls_embedded_idx on client_calls (client, embedded);

-- Backfill: mark already-processed calls based on existing call_chunks data.
update client_calls c set chunked = true
  where exists (select 1 from call_chunks ch where ch.call_id = c.id);

update client_calls c set embedded = true
  where chunked = true
    and not exists (
      select 1 from call_chunks ch
      where ch.call_id = c.id and ch.embedding is null
    );
