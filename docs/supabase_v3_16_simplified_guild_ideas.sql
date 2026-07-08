-- StankyTools v0.3.16
-- Simplified Guild Ideas: title, description, status only.

create extension if not exists pgcrypto;

create table if not exists public.guild_ideas (
  id uuid primary key default gen_random_uuid(),
  guild_code text not null,
  category text not null default 'General',
  title text not null default 'Untitled',
  description text not null default '',
  status text not null default 'New',
  submitted_by text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.guild_ideas alter column status set default 'New';
alter table public.guild_ideas alter column category set default 'General';

update public.guild_ideas
set status = 'New'
where status is null or btrim(status) = '';

alter table public.guild_ideas enable row level security;

do $$
begin
  begin
    alter publication supabase_realtime add table public.guild_ideas;
  exception when duplicate_object then
    null;
  end;
end $$;

create unique index if not exists guild_ideas_id_idx on public.guild_ideas(id);
create index if not exists guild_ideas_guild_code_idx on public.guild_ideas(guild_code);

drop policy if exists "guild_ideas_select" on public.guild_ideas;
create policy "guild_ideas_select" on public.guild_ideas for select using (true);

drop policy if exists "guild_ideas_insert" on public.guild_ideas;
create policy "guild_ideas_insert" on public.guild_ideas for insert with check (true);

drop policy if exists "guild_ideas_update" on public.guild_ideas;
create policy "guild_ideas_update" on public.guild_ideas for update using (true) with check (true);

drop policy if exists "guild_ideas_delete" on public.guild_ideas;
create policy "guild_ideas_delete" on public.guild_ideas for delete using (true);
