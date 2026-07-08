-- StankyTools v0.3.15
-- Guild Ideas + POI/Base delete permissions for owners/officers/admins.

create extension if not exists pgcrypto;

create table if not exists public.guild_ideas (
  id uuid primary key default gen_random_uuid(),
  guild_code text not null,
  category text not null default 'General',
  title text not null default 'Untitled',
  description text not null default '',
  status text not null default 'Reviewing',
  submitted_by text not null default '',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.guild_ideas enable row level security;

alter publication supabase_realtime add table public.guild_ideas;

create unique index if not exists guild_ideas_id_idx on public.guild_ideas(id);
create index if not exists guild_ideas_guild_code_idx on public.guild_ideas(guild_code);

-- Permissive policies for anon-key desktop sync. If your project uses authenticated users,
-- tighten these later to auth.uid()/membership based policies.
drop policy if exists "guild_ideas_select" on public.guild_ideas;
create policy "guild_ideas_select" on public.guild_ideas for select using (true);

drop policy if exists "guild_ideas_insert" on public.guild_ideas;
create policy "guild_ideas_insert" on public.guild_ideas for insert with check (true);

drop policy if exists "guild_ideas_update" on public.guild_ideas;
create policy "guild_ideas_update" on public.guild_ideas for update using (true) with check (true);

drop policy if exists "guild_ideas_delete" on public.guild_ideas;
create policy "guild_ideas_delete" on public.guild_ideas for delete using (true);

-- If RLS is enabled on POI/base tables in your project, these permissive policies keep the app-side
-- owner/officer/member checks from being blocked by Supabase. Desktop app permissions are still
-- enforced in the application UI.
do $$
begin
  if to_regclass('public.guild_pois') is not null then
    alter table public.guild_pois enable row level security;
    drop policy if exists "guild_pois_delete_any_for_app" on public.guild_pois;
    create policy "guild_pois_delete_any_for_app" on public.guild_pois for delete using (true);
    drop policy if exists "guild_pois_select_for_app" on public.guild_pois;
    create policy "guild_pois_select_for_app" on public.guild_pois for select using (true);
    drop policy if exists "guild_pois_insert_for_app" on public.guild_pois;
    create policy "guild_pois_insert_for_app" on public.guild_pois for insert with check (true);
    drop policy if exists "guild_pois_update_for_app" on public.guild_pois;
    create policy "guild_pois_update_for_app" on public.guild_pois for update using (true) with check (true);
  end if;

  if to_regclass('public.guild_bases') is not null then
    alter table public.guild_bases enable row level security;
    drop policy if exists "guild_bases_delete_any_for_app" on public.guild_bases;
    create policy "guild_bases_delete_any_for_app" on public.guild_bases for delete using (true);
    drop policy if exists "guild_bases_select_for_app" on public.guild_bases;
    create policy "guild_bases_select_for_app" on public.guild_bases for select using (true);
    drop policy if exists "guild_bases_insert_for_app" on public.guild_bases;
    create policy "guild_bases_insert_for_app" on public.guild_bases for insert with check (true);
    drop policy if exists "guild_bases_update_for_app" on public.guild_bases;
    create policy "guild_bases_update_for_app" on public.guild_bases for update using (true) with check (true);
  end if;
end $$;
