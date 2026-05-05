# White Paper Analysis Plan

## "Do Semantic Models Turn File-Based Systems into Knowledge Graphs?"

---

## 1. Data Collection

### 1.1 Raw Metrics (from benchmark runner)

| File Pattern | Description |
|--------------|-------------|
| `results/{system}/{phase}/*.json` | Individual task results |
| `results/combined_{timestamp}.json` | Full benchmark run |

### 1.2 Expected Data Fields

```
TaskResult {
  task_id, system, phase, timestamp
  turns, search_ops, latency_ms, tokens
  traversal_quality, explainability, result_quality
  error, notes
}
```

---

## 2. Analysis Dimensions

### 2.1 Performance Metrics

**Primary Comparison:**
- Turns to Answer (lower = better)
- Search Operations (lower = better)
- Latency (lower = better)
- Token Cost (lower = better)

**Visualization:** Bar charts comparing Phase A vs Phase B per system

### 2.2 Quality Metrics

**Traversal Quality:** excellent/good/partial/poor
- Did the system navigate to relevant information?

**Explainability:** full/partial/none
- Can the system justify its answer with sources?

**Result Quality:** correct/partial/incorrect
- Did the answer satisfy the query?

**Visualization:** Stacked bar charts or heatmaps

### 2.3 Task Category Analysis

Compare performance by category:
- Repo Navigation
- Architecture Understanding
- Pattern Retrieval
- Cross-Artifact Reasoning
- Write Operations

### 2.4 Phase Comparison (The Core Question)

**Baseline vs Semantic:**
- Does adding typed entities/relationships improve metrics?
- Which systems benefit most from semantic overlay?

---

## 3. Statistical Analysis

### 3.1 Required Calculations

```python
# Per-system aggregates
{
  "llmwiki_baseline": {"avg_turns": X, "avg_latency": Y, ...},
  "llmwiki_semantic": {"avg_turns": X, "avg_latency": Y, ...},
  "graphify_baseline": {...},
  "graphify_semantic": {...},
  "mempalace_baseline": {...},
  "mempalace_semantic": {...},
}

# Improvement ratios
{
  "llmwiki": {"turns_reduction": 0.15, "latency_improvement": 0.08, ...},
  ...
}
```

### 3.2 Significance Testing

- Sample size: ~10 tasks × 3 systems × 2 phases = 60 data points
- Use paired t-test for baseline vs semantic per system
- Mann-Whitney U for cross-system comparison

---

## 4. White Paper Structure

### 4.1 Executive Summary (1 page)

- Problem statement
- Key findings (3-5 bullet points)
- Implications

### 4.2 Introduction (1-2 pages)

- What is a knowledge graph?
- Current approaches (LLMWiki, Graphify, MemPalace)
- The research question

### 4.3 Methodology (2-3 pages)

- Systems tested
- Task suite description
- Metrics definition
- Experimental design (Phase A/B)

### 4.4 Results (4-6 pages)

- Performance comparison (tables + charts)
- Quality comparison
- Phase A vs Phase B analysis
- Per-category breakdowns

### 4.5 Analysis (3-4 pages)

- What works and why
- When semantics help vs hurt
- System-specific insights

### 4.6 Limitations (1 page)

- Corpus constraints
- Task set bias
- Evaluation subjectivity

### 4.7 Conclusions (1-2 pages)

- Answer to research question
- Recommendations for practitioners
- Future work

### 4.8 Appendices

- Raw data tables
- Task prompts
- System configurations

---

## 5. Visualization Requirements

### 5.1 Required Charts

| Chart | Type | Purpose |
|-------|------|---------|
| Performance by System | Grouped bar | Compare baseline vs semantic |
| Quality Heatmap | Heatmap | Traversal/Explainability/Result by system+phase |
| Task Category Radar | Radar | Multi-dimensional comparison |
| Improvement Delta | Waterfall | Show deltas between phases |
| Token Cost Comparison | Stacked bar | Cumulative cost analysis |

### 5.2 Tools

```bash
# Generate charts from results
python scripts/analyze-results.py --charts --output docs/figures/
```

---

## 6. Output Files

```
experiments/
├── results/
│   ├── raw/
│   │   ├── llmwiki/baseline/*.json
│   │   ├── llmwiki/semantic/*.json
│   │   ├── graphify/...
│   │   └── mempalace/...
│   ├── aggregated/
│   │   ├── system_comparison.json
│   │   ├── phase_comparison.json
│   │   └── category_analysis.json
│   └── figures/
│       ├── performance_comparison.png
│       ├── quality_heatmap.png
│       └── ...
├── docs/
│   └── whitepaper/
│       ├── sections/
│       └── final.md
└── WHITEPAPER_ANALYSIS.md (this file)
```

---

## 7. Running the Full Analysis

```bash
# 1. Run benchmarks
python scripts/run-benchmark.py --all --output results/combined_$(date +%Y%m%d).json

# 2. Generate analysis
python scripts/analyze-results.py --input results/combined_*.json --charts

# 3. Compile white paper
python scripts/compile-whitepaper.py --template docs/whitepaper/template.md
```

---

## 8. Key Questions to Answer

1. **Does explicit semantic modeling improve retrieval?**
   - Look at: turns, search_ops in Phase B vs Phase A

2. **Which system benefits most from semantics?**
   - Compare improvement ratios across systems

3. **What tasks benefit most?**
   - Category-level analysis

4. **Is there a tradeoff?**
   - Latency/cost vs quality

5. **What's the minimum viable ontology?**
   - Which entity/relation types had most impact

---

## 9. Draft Findings (To Validate)

Based on EXPERIMENT_PLAN.md hypotheses:

- LLMWiki: excels at synthesis, lacks strict semantics
- Graphify: excels at structure, needs constraints for reasoning
- MemPalace: efficient routing, needs ontology for full KG

Expected outcome: "Graphs emerge from structure, but knowledge graphs emerge from semantics"

---

## 10. Timeline

| Week | Activity |
|------|----------|
| 1 | Run full benchmark suite |
| 2 | Data cleaning + validation |
| 3 | Statistical analysis |
| 4 | Generate visualizations |
| 5 | Draft white paper sections |
| 6 | Review + refine |
| 7 | Final polish + external review |
| 8 | Publish |