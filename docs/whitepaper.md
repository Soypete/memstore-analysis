# Evaluating Storage Architectures for Context Retrieval in AI Coding Assistants

Author: Miriah Peterson  
Date: May 2026  

---

## Abstract

AI coding assistants can operate without persistent memory; however, in practical software engineering environments, systems that capture and reuse context across repositories can improve efficiency in tasks such as refactoring, dependency analysis, and pattern reuse. This paper evaluates three storage architectures for such context systems: markdown-based storage, full graph materialization, and database-style indexed retrieval. We measure storage size and system-level query latency across a shared task suite. Results show that database-style systems, which support indexed and selective retrieval, significantly outperform systems requiring full dataset materialization. Specifically, indexed retrieval achieved millisecond-level latency and megabyte-scale storage, compared to second-level latency and gigabyte-scale storage for full graph approaches. These findings suggest that storage architecture, particularly the use of indexed retrieval, is the dominant factor in performance for context retrieval systems used in AI-assisted development workflows.

---

## 1. Introduction

AI coding assistants have rapidly evolved in capability, but their effectiveness in real-world engineering environments remains constrained by access to relevant context. While these systems can operate without persistent memory, developers frequently benefit from tools that capture and reuse knowledge across repositories, services, and workflows. In practice, such systems enable reuse of implementation patterns, visibility into cross-service dependencies, and more efficient navigation of large and evolving codebases.

Context retrieval plays a central role in enabling these workflows. Tasks such as refactoring, dependency tracing, and consistency validation often require access to information that spans multiple repositories or historical changes. Without structured mechanisms for retrieving this information, developers and AI systems must repeatedly reconstruct context, leading to increased cognitive load and redundant analysis.

This paper evaluates how different storage architectures affect the performance of context retrieval systems used in AI-assisted development. Rather than focusing on model behavior, the study isolates the impact of storage and retrieval strategy on system-level performance, with an emphasis on latency and storage efficiency.

---

## 2. Related Work

Several approaches have emerged for managing context in AI-assisted development systems. Markdown-based approaches, such as LLM-generated wikis, prioritize human readability and ease of inspection but lack strong guarantees around indexing and retrieval performance. These systems are often effective for documentation-oriented workflows but may degrade in performance as the volume of stored content increases.

Graph-based approaches construct explicit representations of relationships between code elements, including functions, files, and dependencies. These systems offer a rich structural view of the codebase and enable traversal-based queries. However, they frequently rely on full graph materialization, which introduces significant overhead when handling large datasets.

Database-backed approaches instead emphasize indexed storage and selective retrieval. By narrowing the search space prior to data access, these systems aim to minimize the amount of data loaded and processed during query execution. This work compares these approaches under controlled conditions to evaluate their relative performance.

---

## 3. Methodology

### 3.1 Systems Under Test

Three representative systems were selected to reflect the dominant storage paradigms in current AI memory architectures. LLMWiki represents markdown-based storage, where context is maintained as human-readable documents and accessed through text-based search. Graphify represents graph-based storage, in which a full graph of code relationships is constructed and traversed at query time. MemPalace represents database-style retrieval, where context is incrementally indexed and retrieved through structured lookup.

### 3.2 Definition: Database-Style Retrieval

For the purposes of this study, a database-style retrieval system is defined as one that maintains indexed representations of data, supports selective retrieval without loading the full dataset, and performs query-time narrowing prior to data access. This definition allows comparison across systems that differ in representation but share common retrieval strategies.

### 3.3 Context Store Construction

All systems were populated using a shared ingestion pipeline that monitored a local development environment and captured file changes across multiple repositories. As changes were detected, relevant context was extracted and stored, including implementation patterns, cross-service dependencies, and reusable components. This approach reflects a realistic scenario in which context evolves continuously alongside active development.

### 3.4 Metrics and Evaluation

Performance was evaluated using system-level latency, defined as the time required to produce a usable answer, including any data loading and retrieval steps. Storage size was measured as the total footprint of each system. Additional metrics, including search operations and agent turns, were recorded but are not the primary focus of this study.

Two forms of latency were observed: micro-benchmark latency, which reflects tool invocation time, and system-level latency, which includes data loading overhead. All reported results correspond to system-level latency.

---

## 4. Results

### 4.1 Storage Size

The storage footprint of each system differed significantly. MemPalace maintained a compact representation at 8.8 MB, while LLMWiki required 33.9 MB for markdown storage. Graphify, which materializes the full graph structure, required approximately 3.7 GB.

Storage Comparison  
Figure 1: Storage footprint comparison across systems.

---

### 4.2 System-Level Latency

System-level latency varied by several orders of magnitude. MemPalace achieved query times on the order of tens of milliseconds, while LLMWiki required several seconds. Graphify exhibited the highest latency, requiring tens of seconds per query due to the need to load and initialize the full graph.

Latency Comparison  
Figure 2: System-level latency comparison.

---

## 5. Analysis

### 5.1 Impact of Global State Loading

The results indicate that the primary determinant of performance is whether a system requires loading global state prior to query execution. Graphify, which materializes the entire dataset, incurs substantial overhead due to data loading and graph initialization. In contrast, MemPalace avoids this cost by retrieving only relevant subsets of data.

### 5.2 Indexed Retrieval vs Full Materialization

Systems that support indexed retrieval demonstrate consistent performance advantages. By narrowing the search space prior to accessing data, these systems minimize both memory usage and computation time. Full materialization approaches, while expressive, introduce overhead that scales with dataset size and can dominate query latency.

### 5.3 Practical Implications

Efficient retrieval has direct implications for AI-assisted development workflows. Systems that can rapidly access relevant context enable faster refactoring, improved dependency analysis, and reduced developer effort in reviewing and validating changes. These benefits are particularly pronounced in environments with multiple repositories and evolving codebases.

---

## 6. Limitations

This study is limited by its focus on single-turn queries and its emphasis on latency and storage efficiency. Retrieval quality and correctness were not fully evaluated, and the impact of scaling across larger datasets remains an area for future investigation. Additionally, semantic overlays were not implemented in this phase of the study.

---

## 7. Conclusion

This evaluation demonstrates that storage architecture is a critical factor in the performance of context retrieval systems. Systems that rely on indexed retrieval achieve significantly lower latency and storage overhead compared to those requiring full dataset materialization. These findings suggest that database-style retrieval is a more efficient foundation for context systems in AI-assisted development.

---

## 8. Future Work

Future work will explore the integration of semantic indexing techniques, including typed entities and relationships, to improve retrieval quality. Additional evaluation will focus on multi-turn agent interactions, scaling behavior across larger corpora, and the impact of retrieval strategies on downstream reasoning tasks.

---

## References

1. Karpathy, A. LLMWiki  
2. Graphify (GitHub)  
3. MemPalace (GitHub)  

---

## Appendix

All experimental code and data are available at:  
https://github.com/Soypete/memstore-analysis  

---