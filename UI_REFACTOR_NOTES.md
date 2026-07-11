# StankyTools Modern Dashboard Refactor

This build adds and integrates reusable UI widgets without changing database, sync, permissions, navigation, or guild logic.

## Reusable widgets

- `GlassCard`
- `SidebarButton`
- `ModernStatCard` / compatibility `StatCard`
- `MemberCard`
- `QuickActionButton`
- `ModernStatusPill`

The reusable implementation is in `stanky_market/ui/modern_widgets.py`.

## Integration

- Existing `PremiumStatCard`, `QuickActionCard`, and navigation construction sites retain their original APIs.
- Dashboard members now render as `MemberCard` widgets with no avatars or right-side decorative icons.
- Dashboard panels use glass containers with 18px corners and subtle shadows.
- Existing clickable stat-card behavior, signals, permissions, hidden compatibility tables, and refresh methods remain connected.
- SVG icons are stored in `stanky_market/assets/icons` and included conditionally by `StankyTools.spec`.
- Orbitron and Rajdhani are requested by the stylesheet with Segoe UI fallbacks. Bundled TTF files can be added later under `stanky_market/assets/fonts` without code changes.
