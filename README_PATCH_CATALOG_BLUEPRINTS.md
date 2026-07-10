# StankyTools Patch - Catalog Requirements + Blueprint Library

Changes in this package:

- Removed local `Import dune-admin JSON File` and `Import dune-admin Folder` buttons from the Catalog page.
- Catalog now uses web import only for supported public sources.
- Double-clicking a catalog item card opens its crafting/building requirements if recipe data exists.
- If no recipe exists, the app shows a clean message instead of doing nothing.
- Removed the 2D Build planner from Game Manager.
- Replaced Build with a Blueprint Library page.
- Game Manager tabs are now: Overview, Craft, Blueprints, Timers.
- Blueprint Library includes a best-effort `Import Blueprints from Web` hook for blueprint-market style JSON/API/page data.

No private server tools, Guild War Room, memory reading, packet sniffing, DLL injection, or game automation were added.
