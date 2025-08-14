# Agent Instructions: Chat-to-Todo Generator

## Objective
Read chat summary files and generate structured todos.md and tasks.md files that extract actionable items at different granularity levels.

## Input
- Chat summary files (markdown format)
- Located in `documentation/chat/` folder
- Contains project discussions, decisions, and technical requirements

## Output
- `documentation/todos.md` - High-level objectives 
- `documentation/tasks.md` - Specific implementation tasks linked to todos

## Step-by-Step Process

### Step 1: Parse Chat Content
1. **Read the entire chat file thoroughly**
2. **Identify action-oriented language patterns:**
   - "Create", "Build", "Implement", "Design", "Analyze"
   - "We should", "Need to", "Must", "Plan to"
   - "Next steps", "Requirements", "Objectives"
3. **Extract key decisions made:**
   - Approved approaches or designs
   - Technology choices
   - Priority statements
   - Scope definitions
4. **Note technical requirements and constraints**
5. **Identify dependencies and logical sequence**

### Step 2: Extract High-Level Objectives (Todos)
**Criteria for todos (umbrella-level work):**
- Major deliverables or features
- Strategic objectives
- Cross-functional efforts
- Takes multiple days/weeks to complete

**Examples:**
- "Build daily dashboard" (not "Add CSS styling")
- "Create data processing pipeline" (not "Parse CSV file")
- "Analyze historical data patterns" (not "Count rows in spreadsheet")

**Priority Assignment:**
- **HIGH**: Explicitly mentioned as urgent, blocking other work, or business critical
- **MEDIUM**: Important but not blocking, strategic value
- **LOW**: Nice-to-have, future considerations

### Step 3: Extract Specific Tasks
**For each todo identified, break down into specific tasks:**

**Task Criteria:**
- Actionable (can be completed in 1-4 hours)
- Specific (clear completion criteria)
- Technical (implementation details)
- Measurable (clear done/not done state)

**Task Categories:**
- **Analysis**: Research, investigation, data exploration
- **Implementation**: Code, HTML, CSS, file creation
- **Integration**: Connecting systems, data sources
- **Validation**: Testing, verification, quality checks
- **Documentation**: Recording decisions, creating guides

**Task Format:**
```markdown
## [Todo Title]
**Priority: [HIGH/MEDIUM/LOW]** - [Brief justification]

### [Logical Grouping if needed]
- [ ] Specific task with clear completion criteria
- [ ] Another specific task
- [ ] Task with technical details
```

### Step 4: Prioritization Logic
**High Priority Indicators:**
- Words like "critical", "urgent", "blocking", "must", "immediately"
- Dependencies (other work cannot proceed without this)
- Data quality issues affecting core functionality
- Leadership deliverables with deadlines

**Priority Ordering Within Tasks:**
1. Data foundation issues (missing data, calculation errors)
2. Core functionality implementation
3. User interface and experience
4. Nice-to-have features and optimizations

### Step 5: Format Output Files

#### todos.md Structure:
```markdown
# Project Todos

High-level objectives for the [project name].

## High Priority
- [ ] **[Todo item]**

## Medium Priority  
- [ ] **[Todo item]**

## Low Priority
- [ ] **[Todo item]**

## Completed
- [x] **[Completed items]**

---
*Last Updated: [Date]*
```

#### tasks.md Structure:
```markdown
# Project Tasks

Specific implementation tasks organized by todo objectives.

## [Todo Title]
**Priority: [LEVEL]** - [Justification]

### [Optional Subgrouping]
- [ ] Specific task
- [ ] Another task with technical details
- [ ] Task with clear completion criteria

## [Next Todo Title]
...

---
*Last Updated: [Date]*
*Total Tasks: [Count] across [Number] major objectives*
```

## Quality Guidelines

### Todos Quality Checklist:
- [ ] Are todos at the right level of abstraction? (Features, not functions)
- [ ] Do priorities reflect chat discussion context?
- [ ] Are completed items properly marked?
- [ ] Is the scope clear for each todo?

### Tasks Quality Checklist:
- [ ] Can each task be completed independently?
- [ ] Are tasks specific enough to be actionable?
- [ ] Do tasks clearly link to their parent todo?
- [ ] Are technical requirements captured?
- [ ] Are dependencies between tasks clear?

## Special Considerations

### Technical Projects:
- Separate analysis tasks from implementation tasks
- Include data validation and quality checking tasks
- Consider infrastructure and deployment requirements
- Include testing and verification steps

### Data Projects:
- Prioritize data foundation issues first
- Include data quality assessment tasks
- Consider correlation and analysis requirements
- Include visualization and reporting tasks

### Dashboard Projects:
- Separate backend (data processing) from frontend (UI/UX)
- Include responsive design and compatibility tasks
- Consider user experience and accessibility
- Include performance and optimization considerations

## Example Output Pattern

Based on a chat about building an email dashboard:

**Todos extracted:**
- Calculate missing response time data
- Build daily dashboard 
- Create data processing pipeline

**Tasks extracted:**
- Analyze CSV structure differences
- Create KPI cards HTML structure
- Implement data parsing functions
- Build visualization components

## Validation Steps

1. **Cross-check**: Does every task link to a todo?
2. **Completeness**: Are all actionable items from chat captured?
3. **Priority**: Do priorities match chat discussion urgency?
4. **Specificity**: Can someone else complete tasks based on descriptions?
5. **Scope**: Are todos appropriately scoped (not too granular, not too broad)?