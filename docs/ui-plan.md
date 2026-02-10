# UI Upgrade Plan (Vitrine)

## Goals
- Make the project feel like a **product**, not just an API demo.
- Preserve the current “one-file” simplicity (no React/Next) while looking polished.
- Optimize for **GitHub screenshot value**.

## UX Structure (single page)
**Header**
- Title: “Daily Ops Agent”
- Subtitle: “Daily ops brief + alerts + decision memory (mock adapters)”
- Right side: small links: `/docs`, GitHub repo

**Tabs**
1) **Brief** (default)
   - Primary action button: “Generate Daily Brief”
   - Output area:
     - Left: rendered Markdown preview (brief)
     - Right: JSON panel (collapsible)
   - Alerts shown as colored chips/badges

2) **Changes**
   - Buttons: “Snapshot Pages”, “Refresh”
   - Table: URL | last hash | time | status

3) **Memory**
   - Simple form: Decision + Outcome + Day (optional)
   - Button: “Add”
   - List of last 20 memory items

## Visual Design
- Layout: centered container (max-width ~1100px)
- Cards with subtle border + shadow
- Palette:
  - Background: #0b1220
  - Card: #111b2e
  - Primary: #22c55e (green)
  - Accent: #60a5fa (blue)
  - Text: #e5e7eb
- Typography: system font

## Interaction details
- Buttons show loading spinner text (“Generating…”, “Snapshotting…”) and disabled state.
- Errors shown in a red callout.
- Success toast-like message (simple inline banner).

## Deliverables
- Update `GET /` HTML to this layout
- Add small CSS + JS helpers
- Keep endpoints unchanged

## QA checklist
- Click all buttons and ensure:
  - Brief loads and renders
  - Snapshot works
  - Changes list loads
  - Memory list loads
  - Memory add works
- Verify on narrow width (mobile-ish)
