---
type: staged
status: unresolved
reason: "full text blocked (SSRN 403 on both the abstract page and the delivery/PDF endpoint) — screening below is built from WebSearch snippets only, not a fetched primary source, and those snippets themselves may be cross-contaminated with a different paper in the same result set (see caveat below), so this cannot be decided either way yet"
---

Zhong, S., Mei, Z., Li, Z., Jiang, N., Wang, M., & Ivanov, K. (2025). *A Multimodal Deep Learning Framework for Hemiplegic Gait Recognition Using Skeleton and Wearable Sensor Data*. SSRN preprint (not yet peer-reviewed). https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5388982

Surfaced via the 2026-07-28 search for new RQ3 evidence (query: "hemiplegic gait deep learning classical machine learning comparison wearable sensor"). Full text could not be retrieved: the abstract page and a direct SSRN delivery/PDF URL both returned HTTP 403 on every attempt this session. Every fact below is a WebSearch-summarized snippet, explicitly **unverified against a primary source**.

## What search snippets suggest (unverified, and flagged as possibly cross-contaminated)

- Combines skeleton data (apparently from a depth camera), insole-based inertial data, and plantar pressure data in one fusion framework, reported accuracy 92.58%, F1 93.86%.
- **Caveat the searching agent flagged directly**: the WebSearch tool synthesizes one answer across multiple result URLs at once without always attributing which detail came from which source. The specific "visual + inertial + plantar pressure fusion, 92.58%/93.86%" figures could belong to this Zhong et al. SSRN paper, or could have bled over from a different, similarly-worded ScienceDirect result in the same result list ("Exploration of deep learning-driven multimodal information fusion frameworks..."). This ambiguity itself could not be resolved without the actual full text.

## Why this is staged rather than decided

Two independent blockers, either of which alone would already warrant staging rather than a decision: (1) full text is completely inaccessible after multiple real attempts, and (2) even the secondhand description available suggests a skeleton/depth-camera component sits at the core of the fusion framework's headline result, which is exactly the kind of non-wearable modality [[eligibility-criteria|EC1]] excludes — unless a wearable-IMU-only result is also reported separately, which no available snippet confirms either way. Also a non-peer-reviewed SSRN preprint, the same verification tier that led to the Sadeghsalehi 2026 precedent being excluded elsewhere in this project. Needs a resolved full-text fetch before either an Ingest or a clean exclusion is warranted — leaning toward exclusion on the current evidence, but not decided unilaterally from snippets alone.
