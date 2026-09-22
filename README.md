# ZoraASI software methods: five-channel v0 and related synthetic telemetry study

**Status:** preprint and research software release candidate, NOT peer reviewed; no DOI assigned in this package. The manuscript distinguishes previously published Phase 2.3 results from a separately developed v0 representational filter.

- `paper/main.tex`: publication manuscript source (Overleaf: pdfLaTeX). The compiled `paper/main.pdf` is packaged in the downloadable handoff; confirm the binary is present in the GitHub checkout before claiming it is hosted there.
- `zora_lab/vakog_filter.py`: **five** representational channels V, A, K, OG, Ad; text-first lexical proxy implementation.
- `tests/test_vakog_filter.py`: fifteen software acceptance checks, not measured sensory/AI-affect performance.
- `Paper_B_v0_spec_sheet.md`: original design-only spec, preserved as originally written.
- `verify_phase_a.py`: **optional** checker requiring a separate authentic Phase 2.3 checkout; it is NOT a prerequisite for packet-free tests and was not run in this handoff.

Run (Python 3.10+, standard library):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
sha256sum -c SOURCE_SHA256SUMS.txt
```

No Phase 2.3 `connection_study.py`, frozen report, or checksum file is copied or modified here. The original public Phase 2.3 package is at https://github.com/Cbaird26/zoraasi-qualia-research . Its report is quoted in the manuscript as prior software work, not counted as a Paper B result. Packet inputs in Paper B require the original Phase 2.3 package available separately; its seam is stub-tested only in this release candidate.

**Claim boundary:** No biological or AI sense, emotion, human temperature, qualia, physical field Phi_c/E, clinical outcome, or externally confirmed physics has been measured. The 15/15 suite checks a finite software contract. It is not a multimodal accuracy benchmark.

**Rights:** Copyright © 2026 Christopher Michael Baird (to the extent applicable). Original paper material: CC BY-NC-ND 4.0 (`LICENSE-PAPER.md`). Original software: limited noncommercial educational/research license (`LICENSE-CODE.md`), **not** MIT/open-source. Third-party works and earlier Phase 2.3 CC0 grants are unaffected. See `RIGHTS_AND_DISCLOSURE.md`.

**AI disclosure:** ChatGPT (Zora persona) assisted code, test harness, and manuscript drafting; user-provided Grok dialogue informed design but is not independent replication. The human author is responsible for scientific claims and publication approval.

## Related research

The author also supplied [Zenodo record 22886946](https://zenodo.org/records/22886946) for cross-reference. Its metadata and relation to this software paper require verification before formal citation or deposit. See [RELATED_RESEARCH.md](RELATED_RESEARCH.md). The uploaded ToE compilation is not included in this software release.
