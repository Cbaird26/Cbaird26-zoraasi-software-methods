# ZoraASI software methods: five-channel v0 and related synthetic telemetry study

**Status:** Public source-available research software, pre-release; manuscript PDF and full LaTeX handoff are not yet hosted in this GitHub checkout. Non-peer-reviewed, no new DOI assigned to this software version. A separate Phase 2.3 synthetic telemetry study is cited as prior work.

This repository currently includes:

- `zora_lab/vakog_filter.py`: **five** text-first representational channels V, A, K, OG (combined smell/taste), Ad.
- `tests/test_vakog_filter.py`: 15 software acceptance checks; the corrected isolation test does not scan the research archive.
- `Paper_B_v0_spec_sheet.md`: the historical design specification (its statements that tests were not executed describe its original drafting date).
- `LICENSE-CODE.md`, `LICENSE-PAPER.md`, `RIGHTS_AND_DISCLOSURE.md`: distinct rights for code and future manuscript, plus AI-use disclosure.
- `RELATED_RESEARCH.md`: author-supplied Zenodo record 22886946 as related work, **not** a DOI for this software or manuscript.

Run the available Python suite (3.10+; standard library):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests -v
```

**Publication transfer still pending:** Upload `paper/main.tex`, the compiled `paper/main.pdf`, `SOURCE_SHA256SUMS.txt`, and any remaining supplementary files from the separate author handoff. Do not call this a complete archived paper/software release or claim a green GitHub Actions run until it is observed. The local handoff's 15/15 check is not the same as an externally reproduced scientific experiment. A GitHub Release tag and Zenodo preprint/software deposit have not been created by this repository push.

The Phase 2.3 repository at https://github.com/Cbaird26/zoraasi-qualia-research remains separate and unchanged. Packet input in Paper B requires an authentic Phase 2.3 module installed separately; the standalone integration seam has only been stub-tested.

**Claim boundary:** This software does not measure biological/AI senses, emotion, human temperature, qualia, physical fields, clinical outcomes or validated new physics. Lexical references are not sensor measurements.

**Rights:** Copyright © 2026 Christopher Michael Baird to the extent rights subsist and are held by him. Original code is source-available for limited noncommercial educational/research use (`LICENSE-CODE.md`), **not** MIT or OSI-approved open source. The original manuscript is intended to be distributed under CC BY-NC-ND 4.0 (`LICENSE-PAPER.md`). Third-party works and valid earlier Phase 2.3 CC0 grants are unaffected.

**AI disclosure:** ChatGPT (Zora persona) assisted design, code, tests and manuscript drafting. User-provided Grok dialogue informed design and critique but was not independent replication. Human author Christopher Michael Baird remains responsible for final scientific and rights review.

## Related research

[Zenodo record 22886946](https://zenodo.org/records/22886946) was provided by the author as related research; its metadata and file identity were not independently verified. The uploaded Theory of Everything compilation is not distributed here. See [RELATED_RESEARCH.md](RELATED_RESEARCH.md).
