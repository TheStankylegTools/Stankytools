-- StankyTools v1.0 beta - realtime/status support
-- Run this once in Supabase SQL editor before public beta if your guild_pois
-- table was created by an older StankyTools schema.

alter table guild_pois add column if not exists status text not null default 'active';
alter table guild_pois add column if not exists archived_at timestamptz;

-- Keep values consistent with the desktop app.
do $$
begin
  if not exists (
    select 1
    from pg_constraint
    where conname = 'guild_pois_status_check'
  ) then
    alter table guild_pois
      add constraint guild_pois_status_check
      check (status in ('active','friendly','enemy','defeated','gone'));
  end if;
end $$;

-- Optional but recommended for true push-style updates between open apps.
-- Supabase may report that the table is already part of the publication; that is fine.
alter publication supabase_realtime add table guild_members;
alter publication supabase_realtime add table guild_pois;
alter publication supabase_realtime add table guild_bases;
alter publication supabase_realtime add table guild_news;
alter publication supabase_realtime add table guild_links;
alter publication supabase_realtime add table guild_activity;
