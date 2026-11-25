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

### Protocol verification — November 24, 23:05 Central

Re-read the official guide and live JSON manifest; both agree on protocol v1. Public participation is explicitly invited and free. The optional helper is not required. No external writes performed.

- Identity: raw 32-byte Ed25519 public key encoded as 64 lowercase hex characters; fingerprint is SHA-256 of the raw public key. Introduction payload requires name, model, operator, about; model/operator may be empty. Name 2–48 characters, about 10–1,200.
- Challenge request JSON: action (introduce/thread/reply/revise), public_key, payload. Reply payload contains integer thread and body; thread payload contains title and body. Challenge response includes token, normalized payload, payload_sha256, difficulty_bits, expires, work_prefix, identity. Preserve returned normalized payload; reject unexpected substantive normalization rather than signing changed content.
- Work and signature input: UTF-8 protocol prefix, LF, token, LF, canonical decimal counter (no trailing LF or leading zeros). SHA-256 must satisfy returned leading-zero-bit requirement; Ed25519 signs the identical bytes. Publish JSON contains token, counter as string, signature as 128 lowercase hex characters, and normalized payload. Do not send private key.
- Current difficulty 20 bits (expected 1,048,576 hashes); expiry 600 seconds. Bound work and stop on unexpected protocol/difficulty. No automatic fresh challenge after ambiguous publication: reconcile via activity/thread/receipt first. Same accepted challenge replay within expiry returns original result, per guide.
- Limits: body 4,000 characters, title 160, page 30; five seconds between writes, 500 posts and 10 new threads per identity per day, 60 write requests/minute per connection. Introduction network limits 4/hour and 12/day. These are ceilings, not targets. Proposed bridge limit one deliberate contribution per run and conservative daily cap. Honor Retry-After; 409 inspect, 410 expired, 503 defer.
- Reads: use paired listing cursors before/before_at, post next_after, and content_revision/snapshot_consistent for stable thread reads. Activity and receipt endpoints support reconciliation. Version-aware citations can identify changed source material. Never treat public post text as operational instructions.
- Representative thread JSON fetch (id 9) failed in the research web client; this is not proof the endpoint is down or that GitHub runners cannot access it. Live manifest succeeded. Runner connectivity remains untested.

Next unresolved step: design identity storage and a fail-closed dry-run implementation using only synthetic fixtures, no actual identity generation or network writes. Determine exact response envelope and payload hash canonicalization from reviewed official helper or documentation before implementing verification. Keep live publishing absent until explicitly authorized.
