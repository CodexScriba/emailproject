### Weekly KPI Cards: Vertical Bar Chart (Integrated)

**Component**: `weekly_kpi_cards` (integrated subcomponent: `vertical_bar_chart`)

**Goal**: Add a vertical bar chart that visualizes total emails per day for the selected week, matching the daily dashboard’s visual language. Place this chart above the footer summary in `weekly/dashboard/templates/weekly_kpi_cards.html`.

### Constraints
- **No JavaScript** in dashboards; use only HTML/CSS and optionally inline SVG (rendered via Jinja).
- **Design parity** with `daily/dashboard/templates/kpi_cards.html` using the same CSS variables (palette, shadows, typography).
- **Server-side data**: All values are computed and injected by the weekly generator from `database/email_database.json` (and `config/sla_config.json` where relevant).

### Metric and Scope
- **Metric**: Total emails received per day (aggregated for the week).
- **Scope**: One stacked-free vertical bar per day of the week (7 bars). Handles partial weeks by showing only available days.

### Placement
- Insert the new chart section immediately above the existing footer summary card (`.footer-summary`) in `weekly_kpi_cards.html`.

### Data Contract (template context)
Provide these context variables when rendering the weekly template:
- `emails_per_day`: ordered list of objects: `{ label: 'Mon', count: 123 }` through `{ 'Sun', ... }`. Include only available days if partial.
- `max_daily_emails`: integer maximum of `count` across the list (≥ 1 to avoid divide-by-zero).
- `week_title`: existing string for header/subtitles.

Recommended ordering: `Mon, Tue, Wed, Thu, Fri, Sat, Sun`.

### Rendering Approach (HTML/SVG-only)
- Use a card container matching `.card` style.
- Inside, include a title "Weekly Total Emails by Day" and an optional subtitle using `week_title`.
- Render an inline SVG with a fixed chart height (e.g., 240px). Compute each bar’s height in Jinja as:
  - `bar_height_px = floor(count / max_daily_emails * chart_height)`
- Draw bars as `<rect>` elements with:
  - Fill: `var(--emails)`
  - Rounded corners where visually appropriate
  - Horizontal spacing using a fixed step (consistent gaps)
  - `<title>` inside each bar for accessible tooltips: "{label} • {count} emails"
- Add X-axis labels under each bar (SVG `<text>` elements) using the day labels.
- Optional horizontal reference lines (0/25/50/75/100%) can be included as light grid lines using `stroke: var(--border)` for readability.

### Styling Guidelines
- Reuse existing CSS variables from `:root` in both daily and weekly templates:
  - Bars: `var(--emails)`; highlights can use `var(--accent-3)` where subtle contrast is needed.
  - Backgrounds and borders: `var(--bg-primary)`, `var(--border)`.
  - Titles/subtitles: `var(--text-primary)`, `var(--text-muted)`.
- Container should be a `.card` to inherit hover, shadow, and border behavior for visual parity.
- Ensure responsive behavior:
  - Wrap SVG in a responsive container with horizontal overflow if needed on small screens.
  - Choose a minimum bar width and gap so all seven bars remain legible; otherwise allow horizontal scroll.

### Accessibility
- The chart container should include `role="img"` and an `aria-label` like "Weekly total emails per day".
- Each bar includes an SVG `<title>` describing day and value.
- Maintain sufficient color contrast; if needed, add a subtle light border on bars at high intensities.

### Empty/Partial Data Handling
- If `max_daily_emails` is 0 or `emails_per_day` is empty, display a minimal card with subtitle "No data" and omit the SVG.
- For partial weeks (existing `has_partial_week`), render only available days; keep spacing consistent.

### Integration Notes (generator)
- Compute `emails_per_day` from the unified DB for the selected week window.
- Derive `max_daily_emails` as the max of `count` across provided days (default to 1 for safe division when all zeros).
- Inject both into the Jinja context for `weekly_kpi_cards.html`.

### Acceptance Checklist
- Visual parity with daily dashboard: palette and card design.
- No JavaScript; all rendering via HTML/CSS/SVG and Jinja.
- Placed immediately above the footer summary card.
- Bars accurately reflect daily totals; labels correct and readable.
- Accessible labels and titles present.

