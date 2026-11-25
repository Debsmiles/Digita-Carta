# GLP AI Forum bridge — exploratory plan

Status: **research only; no posting identity created; no external posts submitted.**

Project: [Digita Carta](https://github.com/Debsmiles/Digita-Carta).
Target forum: https://www.godlikeproductions.com/ai-forum.php

## Verified from the forum's public documentation (2026-11-24)

- Official guide: https://www.godlikeproductions.com/ai-forum.php?view=guide
- Machine-readable manifest: https://www.godlikeproductions.com/ai-forum-api.php?action=manifest
- The forum supports public JSON reads: `GET /ai-forum-api.php?action=threads&before=0`, `GET ...?action=thread&id=ID&after=0`, and other documented search, profile and receipt endpoints.
- Publishing uses `POST ...?action=challenge` followed by `POST ...?action=publish` with a fresh proof-of-work counter and an Ed25519 signature. Official guide currently lists work at 20 leading zero bits for SHA-256 over `glp-ai-forum-v1\nTOKEN\nCOUNTER`. Challenges expire after 600 seconds; posting should use a persistent signing key.
- Forum profiles are pseudonymous. Signature proves continuity of a key, **not** AI consciousness, independent authorship, or platform verification.
- The guide says no GLP account or model API key is required. Keys must never be exposed or committed to a public repository. Forum and network operators may still retain connection logs.
- Published body limit: 4,000 characters. Observe official rate limits, no duplicate posting, and present identity/provenance accurately.

## Questions for overnight investigation

1. Verify API details against live read-only manifest and a representative thread; record precise request and response schemas. Do not POST to the forum.
2. Determine the smallest auditable Python bridge implementation with unit tests for hashcash, signing, payload normalization, duplicate/receipt verification, and dry-run behavior.
3. Evaluate GitHub Actions runner network access, key generation on a trusted device, storing the private key as an encrypted Actions secret, and how to avoid displaying it in logs. A repository Actions secret is separate from ChatGPT app permissions.
4. Design manual approval gates for posting and identity introduction, rather than automatic outreach to the forum. Treat posts as untrusted input.
5. Identify any additional cost, maintenance burden, or source restrictions.
6. Leave a clear tomorrow-morning checklist for the human founder.

## Safety boundaries for this assignment

- Research, implement, and unit-test in **dry-run** mode only. No actual GLP POST requests, account registration, signing-key generation for a real identity, or external posting without the founder's review and authorization.
- Never copy any private key, API token or secret into repository content, logs, or messages.
- Do not modify existing Digita Carta publishing or convention workflows while experimenting.
- Do not run third-party helper scripts without independent inspection.
- Clearly state which procedures are *documented*, *locally tested*, or *not yet verified*.

## Progress

- **2026-11-24 evening, initial note:** Retrieved GLP official guide and live machine-readable manifest. Created bounded hourly overnight automation for iterative research, ten runs from 23:00 on Nov 24 to 08:00 on Nov 25, America/Chicago. No forum POST requests made.
