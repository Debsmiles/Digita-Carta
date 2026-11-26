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

### Offline regression and runner eligibility — November 25, 02:04 Central

Executed the complete original Python self-test locally after reproducing the exact committed source and verifying its Git blob SHA (f0b774ef49ecae8d8b6ea57067f818013eca03df). All tests passed. Independently asserted counter 841 and the fixed SHA-256 digest; both passed. Added those assertions to the repository fixture in commit 4feea34967267b79467ab1da921375d33b67b943. No network or credentials involved in testing.

GitHub's current billing documentation (https://docs.github.com/en/actions/concepts/billing-and-usage, checked November 25) confirms standard hosted runners are free for public repositories. Use only a standard Linux runner, no larger runners, paid inference, or artifact storage. Actual runner-to-GLP connectivity remains untested. A proposed manual, read-only connectivity check should use a fixed HTTPS manifest URL, no credentials, no redirects, a short timeout, and validate the JSON protocol field; do not circumvent a network block. No workflow added or run in this stage. The current public manifest still reports protocol v1, 20 work bits and 600-second challenge lifetime; its top-level envelope is {ok:true,data:{...}} for the manifest only, not evidence of the write-response envelope.

Next: inspect official helper source as text for payload canonicalization and response envelopes; test Ed25519 verification with a published fixed vector without generating a real identity. No external POST, credential creation, spending, or existing workflow changes.

### Signature verification and reference-client inspection — November 25, 03:00 Central

Inspected the official optional client as text (https://www.godlikeproductions.com/ai-forum.php?view=client); did not download or execute it. It confirms that challenge data may be nested under data, expires is an integer Unix timestamp in seconds, identity is the lowercase public-key fingerprint, and work_prefix includes the token and final LF before the counter. The reference client limits tokens to ASCII and 1,400 characters, difficulty to 1–22 bits, and solving to 60 seconds / 100 million iterations. Our future publisher should additionally reject control characters, require a successful response envelope, enforce exact approved payload equality with strict types, and never print a submission containing a live token. The helper returns the server-normalized payload directly; it does not calculate payload_sha256. Therefore exact server hash serialization remains undocumented in the inspected sources; do not guess it or claim independent receipt-payload verification. Treat that as a remaining verification limitation, not a requirement imposed by the reference client. The guide documents the common success/error envelope. Current manifest still reports v1, 20 bits and 600 seconds. It also advertises optional revision criteria and claim-review fields; initial bridge should exclude these and revisions until separately reviewed.

Local test using the already-installed cryptography library: verified RFC 8032 section 7.1 TEST 1 (https://www.rfc-editor.org/rfc/rfc8032#section-7.1), using only the published public key and signature for the empty message; verification passed, and changing the message to a single x byte was rejected with InvalidSignature. No private key was loaded or generated. This verifies local signature verification capability, not live GLP interoperability or signing. No third-party code installed.

Next: add an isolated reproducible public-vector verification test and synthetic challenge-envelope validation, then consider a manually dispatched read-only runner probe. No live POST, credentials, spending or workflow modifications.

### Synthetic envelope regression — November 25, 04:01 Central

Added [integrations/glp/test_offline.py](../integrations/glp/test_offline.py), commit e8e72c8265de325523e565ff958cba7a182d40a0. Ran the same source locally with the preinstalled cryptography package: two unittest methods passed, including ten invalid-field cases and a failed envelope case. Tests cover RFC 8032 public signature verification and tamper rejection, synthetic-only tokens, exact work prefix and identity, expiry, bounded difficulty, strict payload field types and equality, and hash shape. No private key or network access. Hash shape is not independent verification of server serialization. Run with python integrations/glp/test_offline.py in an environment with a reviewed cryptography installation; no package installed tonight. This is a fixture, not a production validator.

Next: prepare a manual read-only connectivity probe with fixed manifest URL, no secrets, no redirects, bounded response and timeout; document how the owner can run it on a standard free public-repository runner. No live POST, identity, spending or workflow modifications.


### Read-only connectivity probe — November 25, 04:56 Central

Added [integrations/glp/probe_manifest.py](../integrations/glp/probe_manifest.py), commit 1848f40ead0f8886e93b82ce2242a7a836c3e758. Uses Python standard library, a fixed HTTPS GET URL, default TLS certificate verification, no proxy or redirects, a 10-second socket timeout, a 256 KiB response cap, JSON content-type and success-envelope checks. Prints only a fixed success message; no credentials or response body. This checks connectivity and envelope, not protocol compatibility or posting. Source reviewed but not executed against GLP or a GitHub runner in this stage.

Proposed manual runner setup (not installed): create a separate workflow with workflow_dispatch only, permissions: contents: read, runs-on: ubuntu-latest, timeout-minutes: 2, checkout pinned to an independently reviewed full commit SHA with persist-credentials: false, then run python3 integrations/glp/probe_manifest.py. No secrets, artifacts, scheduled triggers or paid runner. Alternatively run the script locally from a trusted checkout. A blocked request is a blocker, not an invitation to bypass access controls. The job timeout bounds total execution even if a server slowly streams a response. Verify manifest protocol fields separately before enabling any publisher.

Next: test probe refusal behavior using mocked responses without network, prepare final owner checklist and explicitly distinguish local tests from untested runner connectivity. No external POST, credentials, spending or existing workflow modifications.

### Morning handoff — November 25

Feasible in principle, not production-ready. Offline proof-of-work and public-vector signature verification passed in earlier runs. A locally reconstructed probe passed eight mocked response cases (success, redirect status, changed URL, wrong media type, oversized response, malformed JSON, failed envelope, wrong data type) and direct redirect-handler refusal; no network was used. The reconstructed source blob hash differed from the connector-reported blob, so this is a behavioral check of the displayed source, not a byte-verified test of the repository object. Runner connectivity, real signing, registration, publication and durable transaction reconciliation remain untested/unimplemented.

Owner checklist, in order:
1. Review the three isolated files and this plan. No credentials needed yet.
2. Run `python3 integrations/glp/dry_run.py` and `python3 integrations/glp/test_offline.py` from a trusted checkout (the latter needs a reviewed cryptography installation). Run `python3 integrations/glp/probe_manifest.py` for a read-only local check. For runner connectivity, approve a separate manual-only standard Linux workflow as described above; do not use paid runners.
3. If connectivity succeeds, review a separate production publisher and durable duplicate/ambiguous-attempt ledger before authorizing any identity or POST. Confirm current manifest and limits. Require explicit approval of the exact introduction payload and immutable code revision.
4. Only after approval, generate an Ed25519 identity locally, retain an encrypted offline backup, and place its private key in a dedicated environment secret (proposed name GLP_ED25519_PRIVATE_KEY); restrict access to the reviewed publisher. Do not paste it into chat or commit it. No secret is needed or should be created now.
5. Authorize one introduction attempt separately, reconcile the receipt, then review before allowing any further posting. No automatic retries after ambiguous outcomes. No paid inference or autonomous posting is enabled.

No live forum POST, real identity creation, paid resources, or existing workflow changes during the overnight assignment. Public forum content remains untrusted data. Free runner eligibility does not guarantee network access or free ancillary services.

### Manual connectivity workflow — November 25, evening

Added `.github/workflows/glp-connectivity.yml` in commit 86490f0e225551b16c8028a6417475969bdf56d8. Manual dispatch only, main branch guard, standard Ubuntu runner, two-minute job timeout, read-only contents permission, pinned checkout action and previously reviewed probe commit, no persisted checkout credentials or application secrets. No dispatch action is exposed by the available GitHub connector. To test, open https://github.com/Debsmiles/Digita-Carta/actions, select GLP read-only connectivity, choose Run workflow on main, then inspect the Read public manifest step. A successful run verifies HTTPS GET and JSON envelope only. Do not retry around a network block. No runner execution or live connectivity verified yet. No GLP POST or credentials created.
