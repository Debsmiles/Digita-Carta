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

### Identity and transaction design — November 25, 00:02 Central

Proposed architecture (not yet deployed): keep the research/drafting agent separate from a deterministic publisher. The agent produces a proposed action and exact payload in an isolated outbox; a future manually authorized publisher consumes a specific immutable commit and proposal digest. Never execute text from the proposal or forum. No live publishing code or workflow is enabled in this stage.

- Identity: after explicit approval, generate one Ed25519 key on a trusted owner-controlled device using a reviewed standard cryptographic implementation. Keep an encrypted offline backup; derive the raw 32-byte public key and fingerprint locally. Store the private key only in a dedicated GitHub environment secret (prefer environment-scoped access and required review where supported). Public fingerprint may be recorded separately. No key generation performed tonight. Never use a general GitHub token as the forum identity.
- Publisher isolation: no model API, no access to unrelated secrets, read-only repository token unless a narrowly scoped receipt write is separately justified. Do not expose secrets to pull requests, fork code, arbitrary refs or untrusted actions. Pin reviewed dependencies and action revisions; do not interpolate forum or proposal text into shell scripts. Restrict HTTPS requests to the exact documented host and endpoint; reject redirects, cap response size, set timeouts.
- Transaction state: proposal digest (action + exact approved payload + identity fingerprint), approved commit, state (pending/approved/challenged/publish-attempted/confirmed/ambiguous/rejected), timestamp and confirmed receipt/post identifier. Persist intent before any future publish attempt. Use one publisher concurrency group, no cancellation of in-flight publication. A duplicate digest or unresolved ambiguous attempt blocks a new publish. Reconcile using public receipt/activity/thread reads before retrying. Never store challenge tokens, private keys or signatures in public logs/state. A crash between publish and receipt persistence must remain ambiguous, not silently reset to pending.
- Challenge validation: check protocol version, exact intended normalized payload, identity, token type/size, expiry and bounded difficulty before solving. Compare semantic fields strictly; reject unknown or changed fields. Use monotonic deadline and bounded iterations, canonical decimal counter, and leading-zero-bit check including non-byte-aligned difficulties. Sign only the documented work bytes after local proof verification. Payload hash canonicalization and exact response envelope remain unresolved; do not invent a canonical JSON encoding.
- Dry-run implementation boundary: pure functions for work-message construction, bit verification, bounded search, proposal digest and state transitions; synthetic fixtures only, no network client or secret loading. Use fixed public test vectors rather than generating a real identity. Later test signature verification against a published Ed25519 vector, with a reviewed local crypto library if available. Dry-run must never accept a switch that enables live writes.
- Cost: no paid inference or new accounts. Before any runner workflow, verify public-repository runner eligibility and applicable usage limits; no workflow execution is authorized to incur charges.

Next: implement and test pure offline primitives in a separate integration directory; then review runner feasibility and exact manifest schema. No external POST, credential creation or workflow changes in this stage.

### Offline proof-of-work fixture — November 25, 01:04 Central

Created [integrations/glp/dry_run.py](../integrations/glp/dry_run.py), commit 65bda7aab8d68ca46e5d09bdfaef5d4d30296f9f. Standard-library-only, no network, signing, secret access or live mode. It checks exact LF-delimited ASCII work bytes, canonical decimal counters, leading zero bits (including partial bytes), and bounded synthetic search. The solver refuses non-synthetic tokens and difficulty above 12 bits. Embedded self-tests cover boundaries and refusal behavior; the full committed self-test has not yet been executed. An independent local Python calculation verified the synthetic 10-bit fixture: token synthetic-test, first counter 841, SHA-256 00074e81ca20f35e98a72c0a318cb33457521ed08dd0a0a346a5675e62095024. No live challenge was obtained.

Next: execute the exact committed fixture locally, strengthen tests with the fixed expected counter/hash, then assess GitHub runner eligibility and read-only connectivity. Payload hash normalization, signature verification and live transport remain unimplemented. No existing workflows changed, no credentials created, no money spent.
