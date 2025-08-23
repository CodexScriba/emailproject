# Weekly KPI Cards: Vertical Bar Chart — Todo

## User Stories
- As a weekly dashboard viewer, I want to see total emails per day so I can quickly spot peak and low activity days across the week.
- As a manager, I want the chart to match the daily dashboard’s visual language so the UI feels consistent.
- As a keyboard and screen reader user, I want descriptive labels/titles so the chart is accessible.
- As a mobile user, I want the chart to remain legible and horizontally scrollable when needed.

## Phase 1: Placement & Structure (Foundation)
- [ ] Insert a new chart section immediately above `.footer-summary` in `weekly/dashboard/templates/weekly_kpi_cards.html`.
- [ ] Wrap the chart in a `.card` to inherit shadows, borders, and hover behavior.
- [ ] Add title “Weekly Total Emails by Day” and subtitle using `{{ week_title }}`.
- [ ] Provide a responsive wrapper that allows horizontal overflow on small screens.

## Phase 2: Data Contract & Generator (Server-Side)
- [ ] Compute `emails_per_day`: ordered list of `{ label: 'Mon'..'Sun', count: int }`, include only available days for partial weeks.
- [ ] Compute `max_daily_emails`: integer max of `count` across provided days; default to `1` to avoid divide-by-zero.
- [ ] Inject `emails_per_day`, `max_daily_emails`, and existing `week_title` into Jinja context for `weekly_kpi_cards.html`.
- [ ] Ensure day ordering: `Mon, Tue, Wed, Thu, Fri, Sat, Sun`.

## Phase 3: Rendering (HTML/SVG-only)
- [ ] Render inline SVG with fixed chart height (≈240px) inside the card.
- [ ] For each day, compute bar height in Jinja: `bar_height_px = floor(count / max_daily_emails * chart_height)`.
- [ ] Draw bars with `<rect>` using `fill: var(--emails)`; add rounded corners where appropriate; use consistent horizontal step/gaps.
- [ ] Add `<title>` inside each bar for tooltips: `"{label} • {count} emails"`.
- [ ] Add X-axis labels under each bar with SVG `<text>` using the day labels.
- [ ] Optional: light horizontal reference lines at 0/25/50/75/100% using `stroke: var(--border)`.

## Phase 4: Styling & Responsiveness
- [ ] Reuse CSS variables from `:root` (daily parity): `--emails`, `--bg-primary`, `--border`, `--text-primary`, `--text-muted`.
- [ ] Keep container `.card` for parity with daily design and existing typography/shadows.
- [ ] Ensure small-screen readability: minimum bar width and gap; allow horizontal scroll if seven bars don’t fit.
- [ ] Maintain sufficient color contrast; add subtle bar stroke/border at high intensities if needed.

## Phase 5: Accessibility
- [ ] Chart container includes `role="img"` and `aria-label="Weekly total emails per day"`.
- [ ] Each bar has an SVG `<title>` describing day and value.
- [ ] Preserve keyboard focus order; ensure labels are readable and sized appropriately.

## Phase 6: Empty/Partial Data Handling
- [ ] If `emails_per_day` empty or `max_daily_emails == 0`, render a minimal card with subtitle “No data” and omit the SVG.
- [ ] For partial weeks (`has_partial_week` exists), render only available days; keep consistent spacing among visible bars.

## Phase 7: QA & Acceptance
- [ ] Visual parity with daily dashboard: palette and card design.
- [ ] No JavaScript; rendering via HTML/CSS/SVG and Jinja only.
- [ ] Placed immediately above the footer summary card.
- [ ] Bars accurately reflect daily totals; labels correct and readable.
- [ ] Accessible labels and titles present.

## Technical Specifications
- **Files**:
  - `weekly/dashboard/templates/weekly_kpi_cards.html` (insert SVG chart card)
  - `weekly/scripts/generate_weekly_dashboard.py` (compute and inject `emails_per_day`, `max_daily_emails`)
- **Data contract**:
  - `emails_per_day`: list of `{ label: 'Mon'..'Sun', count: int }`, only available days if partial
  - `max_daily_emails`: integer `max(count)` across days (≥ 1 safe default)
  - `week_title`: existing string for subtitle
- **Rendering**:
  - Chart height: ~240px constant
  - Bars: `<rect>` with `fill: var(--emails)`; rounded corners; fixed step/gap
  - Labels: SVG `<text>` under bars
  - Grid lines: optional 0/25/50/75/100% with `stroke: var(--border)`
- **Accessibility**:
  - Wrapper `role="img"` + `aria-label`
  - Each bar includes `<title>`
- **Responsive**:
  - Horizontal overflow on small screens; min bar width and spacing

## Out of Scope
- No JavaScript for this chart.
- Do not alter unrelated dashboard sections.
