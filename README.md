# Portfolio Construction and Factor Research

**Liuyu Xiong · CQF final project · January 2024**

An academic Python study of portfolio allocation, exploratory equity factors and Black–Litterman investor views.

## Start with the tested 2026 revision

[Run the revised research components and tests](revised/README.md). The public release separates the **original 2024 coursework** from an **AI-assisted publication revision dated 12 September 2026**. The revision contains point-in-time selection checks, consistent return units, wealth-index drawdown, seeded portfolio simulation, full-factor OLS and a simplified walk-forward demonstration.

**28 unit/regression tests passed locally.** The deterministic demonstration uses only artificial data, with 10 assets, 104 weekly return periods, a 52-period training window and 52 evaluation periods. These are software tests, not the original project's market results. [Test evidence](revised/TEST_RESULTS.md).

## Research at a glance

- **525 weekly price observations**, covering 2 October 2009 to 18 October 2019.
- **10 US equities and three market benchmarks**.
- **10,000** randomly generated long-only allocations.
- HML/SMB-style spread analysis and **60-week** rolling regressions.
- Black–Litterman allocation comparisons under three illustrative risk-aversion settings.

## Review the work

- [Public research report](reports/Research_Report_Public.pdf)
- [Original factor-research notebook, outputs removed](notebooks/FAMA_archival.ipynb)
- [Original Black–Litterman notebook, outputs removed](notebooks/BL_archival.ipynb)
- [Evidence mapping and material implementation limitations](docs/EVIDENCE_AND_LIMITATIONS.md)
- [Required input schema](docs/DATA_DICTIONARY.md)
- [Data rights and publication notes](docs/PUBLICATION_NOTES.md)

## Status of the notebooks

The notebooks preserve the original numerical source for inspection. Cell outputs, execution counts, attachments and metadata have been cleared. They are **archival coursework**, not production-ready or independently validated trading systems. Their issues are corrected or constrained in separately dated revised components; they are not silently rewritten. Review the documented issues before interpreting the archived calculations.

Wind input workbooks are not redistributed. The notebooks are therefore not self-contained, and no historical performance is claimed as reproduced. Inspect them directly on GitHub; executing them requires separately authorized data and local Python dependencies. The FAMA notebook includes a FRED network call.

## Dependencies referenced by the source

Python, pandas, NumPy, Matplotlib, SciPy, statsmodels, seaborn, pandas-datareader, openpyxl and imageio. Original package versions were not recorded; this list is descriptive rather than a tested or pinned runtime.

Academic research only. No claim of live returns, verified alpha, investment advice or endorsement by CQF or a data provider.
