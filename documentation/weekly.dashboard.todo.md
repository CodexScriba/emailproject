# Weekly Dashboard Implementation TODO List

## Overview
Comprehensive action items for implementing the weekly dashboard based on `documentation/weekly.dashboard.plan.md`
- **Source of Truth:** `database/email_database.json`
- **Architecture:** Follows existing daily dashboard patterns (HTML/CSS only, no JavaScript)
- **Output:** `weekly/output/weekly_dashboard_YYYY-Www.html`

---

## Phase 1: Project Setup & Directory Structure

### 1.1 Create Directory Structure
- [x] Create `weekly/` directory at project root ✅ **COMPLETED**
- [x] Create `weekly/scripts/` subdirectory ✅ **COMPLETED**
- [x] Create `weekly/templates/` subdirectory ✅ **COMPLETED**
- [x] Create `weekly/output/` subdirectory ✅ **COMPLETED**

### 1.2 Configuration Setup
- [x] Review `config/sla_config.json` for business hours settings ✅ **COMPLETED** (7-21, all 7 days)
- [ ] Document any weekly-specific configuration needs
- [x] Ensure business hours (7 AM - 9 PM) are properly configured ✅ **COMPLETED**

---

## Phase 2: Data Processing Script

### 2.1 Create Main Generator Script
**File to Create:** `weekly/scripts/generate_weekly_dashboard.py`

#### Core Functions to Implement:
- [ ] `load_sla_config()` - Reuse from `daily/scripts/generate_dashboard.py`
- [ ] `load_email_database()` - Read from `database/email_database.json`
- [ ] `get_week_dates(week_str)` - Parse ISO week string (e.g., "2025-W34")
- [ ] `get_last_7_days()` - Get date range for last 7 days option
- [ ] `filter_week_data(database, start_date, end_date)` - Extract week's data

#### Week Aggregation Functions:
- [ ] `calculate_weekly_kpis(week_data)` - Aggregate KPIs across 7 days
  - Total emails for week
  - Average emails per day
  - Average unread count (weighted)
  - Average response time (weighted)
  - Overall SLA compliance percentage
  
- [ ] `aggregate_daily_totals(week_data)` - Sum emails by day
  - Returns: {day: total_emails} for Mon-Sun
  
- [ ] `create_hourly_heatmap_data(week_data)` - Build hour×day grid
  - 7 columns (days) × 14-15 rows (business hours)
  - Returns: 2D array of email counts
  
- [ ] `aggregate_response_time_by_hour(week_data)` - Weekly hourly averages
  - Reuse logic from `daily/scripts/generate_dashboard.py`
  
- [ ] `calculate_response_time_distribution(week_data)` - Weekly distribution
  - Categories: Very Fast, Fast, Moderate, Slow, Very Slow, Critical
  
- [ ] `calculate_response_time_percentiles(week_data)` - P25, P50, P75, P90, P95
  
- [ ] `aggregate_two_hour_blocks(week_data)` - Weekly 2-hour metrics
  - Reuse `aggregate_two_hour_intervals()` logic

#### Analysis Functions:
- [ ] `find_best_worst_days(week_data)` - Identify performance extremes
  - Best SLA day
  - Worst response time day
  - Busiest/quietest days
  
- [ ] `find_peak_indicators(week_data)` - Identify peak periods
  - Peak email hour (day + hour)
  - Worst response time (day + hour)
  - Max unread backlog (day + hour)
  
- [ ] `build_daily_sla_table(week_data)` - Day-by-day SLA compliance

#### CLI Interface:
- [ ] Implement argument parser
  - `--week YYYY-Www` (ISO week format)
  - `--last-7-days` (last 7 calendar days)
  - `--validate-only` (check data availability)
  - `--list-weeks` (show available weeks)

#### Output Functions:
- [ ] `save_dashboard(html_content, week_identifier)`
  - Save to `weekly/output/weekly_dashboard_YYYY-Www.html`
  - Create/update `weekly/output/latest.html` symlink

---

## Phase 3: Template Development

### 3.1 Main Template File
**File to Create:** `weekly/templates/weekly.html`

#### Template Sections to Implement:
- [ ] HTML boilerplate with embedded CSS (reuse daily dashboard styles)
- [ ] Header section with week title ("Email Performance Dashboard Week #34")
- [ ] KPI cards container
- [ ] Charts grid container
- [ ] Summary cards container
- [ ] AI insights section placeholder

### 3.2 Component Templates (Can be in main file or separate)
**Consider creating partial templates or sections within main template:**

#### KPI Cards Section:
- [ ] Total Emails card (modified for week total)
- [ ] Average Emails Per Day card (NEW)
- [ ] Avg Unread Count card (reuse daily logic)
- [ ] Avg Response Time card (reuse daily logic)
- [ ] SLA Compliance card (reuse daily logic)

#### Charts Section:
- [ ] Daily Email Volume bar chart (NEW)
- [ ] Hourly Email Distribution heatmap (NEW)
- [ ] Response Time by Hour chart (adapt daily version)
- [ ] Response Time Distribution chart (adapt daily version)
- [ ] Response Time Percentiles chart (adapt daily version)
- [ ] 2-Hour Email Metrics table (adapt daily version)

#### Summary Section:
- [ ] Best/Worst Day cards grid (NEW)
- [ ] Daily SLA Compliance table (NEW)
- [ ] Weekly Peak Indicators cards (NEW)

### 3.3 CSS Styling
**Reuse from:** `daily/dashboard/templates/kpi_cards.html`

#### New Styles to Add:
- [ ] Heatmap grid styles
  - Cell colors (gradient from light to dark)
  - Cell hover effects
  - Grid layout
  
- [ ] Bar chart styles
  - Bar colors and heights
  - Labels and values
  
- [ ] Summary card styles
  - Best/worst indicators
  - Peak indicator badges

---

## Phase 4: Component Implementation

### 4.1 Component 1: Title and KPI Cards
- [ ] Implement week number calculation from date
- [ ] Adapt KPI card HTML structure from daily dashboard
- [ ] Calculate weekly aggregates for each KPI
- [ ] Apply appropriate color coding based on thresholds

### 4.2 Component 2: Daily Email Volume Chart
- [ ] Create SVG bar chart structure
- [ ] Calculate max height for scaling
- [ ] Add day labels (Mon-Sun)
- [ ] Display email counts on bars
- [ ] Apply consistent styling

### 4.3 Component 3: Hourly Email Distribution Heatmap
- [ ] Create grid structure (7×14-15 cells)
- [ ] Calculate color intensity based on email volume
- [ ] Add hour labels (7AM-9PM)
- [ ] Add day headers
- [ ] Display counts in cells
- [ ] Implement color gradient scale

### 4.4 Component 4-7: Response Time Analytics
- [ ] Adapt response time by hour chart
- [ ] Adapt response time distribution
- [ ] Adapt response time percentiles
- [ ] Adapt 2-hour metrics table
- [ ] Ensure weekly aggregation logic

### 4.5 Component 8: Best/Worst Day Summary
- [ ] Create 4-card grid layout
- [ ] Calculate best SLA day
- [ ] Calculate worst response time day
- [ ] Find busiest/quietest days
- [ ] Apply appropriate styling/colors

### 4.6 Component 9: Daily SLA Compliance Table
- [ ] Create table structure
- [ ] Calculate daily SLA percentages
- [ ] Add status badges (green/yellow/red)
- [ ] Apply responsive table styling

### 4.7 Component 10: Weekly Peak Indicators
- [ ] Find peak email hour across week
- [ ] Find worst response time period
- [ ] Find max unread backlog point
- [ ] Create indicator cards/badges

---

## Phase 5: AI Analysis Integration (Phase 2)

### 5.1 AI Analysis Function
**Add to:** `weekly/scripts/generate_weekly_dashboard.py`

- [ ] Create `generate_ai_analysis(week_data)` function
- [ ] Implement prompts for pattern analysis
- [ ] Format AI responses into structured sections
- [ ] Add error handling for AI service failures
- [ ] Cache results to avoid repeated calls

### 5.2 AI Insights Template Section
**Add to:** `weekly/templates/weekly.html`

- [ ] Executive Summary section
- [ ] Key Insights bullet points
- [ ] Performance Highlights
- [ ] Areas for Improvement
- [ ] Recommendations list
- [ ] Risk Indicators warnings

---

## Phase 6: Testing & Validation

### 6.1 Data Validation
- [ ] Test with various week selections
- [ ] Handle missing days in week gracefully
- [ ] Validate calculations against daily dashboards
- [ ] Check edge cases (partial weeks, holidays)

### 6.2 Visual Testing
- [ ] Verify all charts render correctly
- [ ] Check responsive design
- [ ] Validate color coding logic
- [ ] Test with different data volumes

### 6.3 CLI Testing
- [ ] Test `--week` parameter with various formats
- [ ] Test `--last-7-days` option
- [ ] Test `--validate-only` flag
- [ ] Test `--list-weeks` functionality

---

## Phase 7: Documentation & Deployment

### 7.1 Documentation
**File to Create:** `weekly/README.md`

- [ ] Usage instructions
- [ ] CLI parameter documentation
- [ ] Architecture overview
- [ ] Troubleshooting guide
- [ ] Example outputs

### 7.2 Integration
- [ ] Update main project README
- [ ] Add weekly dashboard to `documentation/architecture.md`
- [ ] Create sample outputs for testing
- [ ] Document in `.windsurf/workflows/` if needed

---

## Files to Reuse (with modifications)

### From Daily Dashboard:
1. **`daily/scripts/generate_dashboard.py`** ✅ **EXISTS**
   - KPI calculation logic
   - Response time analysis functions
   - 2-hour aggregation logic
   - SLA compliance calculations

2. **`daily/dashboard/templates/kpi_cards.html`** ✅ **EXISTS**
   - HTML structure for KPI cards
   - CSS styles for cards and charts
   - Color coding logic
   - Animation effects

3. **`config/sla_config.json`** ✅ **EXISTS**
   - Business hours configuration (7-21, all 7 days)
   - SLA thresholds (30 unread, 120 min response)
   - Target values (85% SLA compliance, 60 min response)

---

## Files to Create

### New Files:
1. `weekly/scripts/generate_weekly_dashboard.py` - Main generator
2. `weekly/templates/weekly.html` - Main template
3. `weekly/README.md` - Documentation
4. `weekly/output/` - Output directory (generated files)

---

## Files to Edit

### Existing Files to Update:
1. **`documentation/architecture.md`**
   - Add weekly dashboard section
   - Update data flow diagrams
   - Document aggregation strategy

2. **Main project `README.md`** (if exists)
   - Add weekly dashboard usage
   - Update feature list

---

## Execution Order

### Recommended Implementation Sequence:
1. **Phase 1:** Setup directory structure (5 min)
2. **Phase 2:** Create data processing script skeleton (2 hours)
3. **Phase 3:** Develop templates with placeholder data (2 hours)
4. **Phase 4:** Implement components one by one (4 hours)
5. **Phase 6:** Test with real data (1 hour)
6. **Phase 7:** Documentation (30 min)
7. **Phase 5:** AI integration (optional, 2 hours)

**Estimated Total Time:** 10-12 hours for MVP (Phases 1-4, 6-7)

---

## Success Criteria

### MVP Completion:
- [ ] Weekly dashboard generates successfully
- [ ] All 10 core components render correctly
- [ ] Data aggregation matches daily dashboard totals
- [ ] CLI interface works for week selection
- [ ] Output saved to correct location
- [ ] Latest.html symlink created

### Full Completion:
- [ ] AI analysis integrated (Phase 5)
- [ ] Documentation complete
- [ ] All edge cases handled
- [ ] Performance optimized for large datasets
