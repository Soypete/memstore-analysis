# Results

This directory stores collected metrics and benchmark results from experiment runs.

## Files

| File | Description |
|------|-------------|
| `baseline.csv` | Phase A (no ontology) results |
| `semantic.csv` | Phase B (with ontology) results |
| `comparison.csv` | Side-by-side comparison |
| `summary.json` | Aggregated metrics |

## Format

Results are logged in CSV with the following columns:

```csv
date,system,phase,task,turns,search_ops,latency_ms,token_cost,result_quality
2026-04-17,LLMWiki,baseline,"find auth implementation",3,5,1200,4500,Correct
```

## Adding Results

1. Run experiment tasks
2. Log results using template in `logs/`
3. Export metrics to CSV

```bash
# Export results
python -m experiments export-results --phase baseline --output results/baseline.csv
```