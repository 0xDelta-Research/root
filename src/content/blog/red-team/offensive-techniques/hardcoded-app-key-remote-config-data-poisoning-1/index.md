---
title: "Hardcoded App Key: Unauthenticated Remote Config Exposure and Data Poisoning in a Mobility Android App"
description: "A hardcoded app key inside an analytics SDK exposed feature flags and allowed arbitrary event injection in an Android fleet-management app — with zero authentication."
pubDate: 2026-09-09
author: "E0B3"
team: "Red Team"
category: "Offensive Techniques"
tags: ["Bug Bounty", "Mobile Security", "Reverse Engineering", "Hardcoded Credentials", "Data Poisoning"]
risk: "HIGH"
---

## Contents_Index

- [About the Operator](#about-the-operator)
- [Executive Summary](#executive-summary)
- [Target Context](#target-context)
- [Technical Overview](#technical-overview)
  - [Attack Vector](#attack-vector)
- [Phase 1: Hunting Through Smali](#phase-1-hunting-through-smali)
- [Phase 2: The Key Becomes a Door](#phase-2-the-key-becomes-a-door)
- [Impact](#impact)
- [Detection & Mitigation (Blue Team Perspective)](#detection--mitigation-blue-team-perspective)
- [Indicators of Compromise (IOCs)](#indicators-of-compromise-iocs)
- [Behind the Hunt](#behind-the-hunt)
- [Conclusion](#conclusion)

---

## About the Operator

Hi, I'm E0B3. I'm a student in the Systems Analysis and Development program (ADS) at IFBA, and I work as a cybersecurity researcher with a focus on bug bounty. This report documents a finding conducted in a two-person team alongside operator RWX_GHOST, within the authorized scope of a private coordinated disclosure program.

---

## Executive Summary

This report documents a **Sensitive Data Exposure** and **Broken Authentication** vector identified in the official Android app of a large mobility-sector company, discovered during an authorized bug bounty engagement conducted as a two-person team.

The flaw resides in a **hardcoded app key** belonging to a self-hosted analytics/telemetry SDK, embedded directly in the binary distributed to millions of users. That single key was enough to (1) read internal A/B testing configuration and unreleased feature flags, and (2) inject arbitrary analytics events into the **production** server — with no validation of origin, session, or app signature.

`Estimated CVSS: 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)`

---

## Target Context

The target of the engagement was the official Android app for remote vehicle fleet management from a large mobility company, distributed at scale — millions of active installs. The investigation started as surface mapping: cataloging the third-party SDKs embedded in the binary and evaluating, for each one, the authentication model exposed to the client.

This article documents the discovery, the technique used, the real impact, and remediation recommendations — without exposing sensitive production data or identifying the company involved, since the finding was reported within a private bug bounty program.

---

## Technical Overview

Like any app of this scale, the target depends on third-party services for telemetry and product experimentation — in this case, a self-hosted analytics SDK, a common choice for companies that don't want to rely on solutions like Firebase or Mixpanel.

This type of SDK works with a simple authentication model: each application receives an app key, which acts as an API key. It identifies the app to the server and authorizes sending — and, depending on endpoint configuration, also reading — data. The problem starts when that key, which should be treated as an application secret, is embedded directly in the binary: any decompilation process exposes it entirely, with no additional exploitation required.

### Attack Vector

1. **Target:** users of the official remote vehicle fleet-management app (Android).
2. **Surface:** self-hosted analytics SDK embedded in the binary, present across multiple environments (production, pre-production, distinct regions) within the same APK.
3. **Exploitation prerequisite:** none. The key, once extracted, is valid for any attacker, with no user authentication required.

---

## Phase 1: Hunting Through Smali

With the APK in hand, the workflow followed classic Android recon: decompilation with apktool, converting Dalvik bytecode into smali — a near 1:1 textual representation of the bytecode, browsable and "greppable."

Instead of reading class by class, the approach was to search directly for strings resembling tokens or hashes within the smali bytecode, filtering out the inevitable noise: signature hashes, SHA values used for integrity checks, and all the legitimate cryptographic material any app carries.

```
grep -rniE "(app_key|apiKey|secret|token)\s*=\s*\"[a-z0-9]{20,}\"" target-app_decompiled/
```

> **⚠️ SECURITY NOTE:** commands, paths, and real file names have been generalized in this public version. The binary and the company involved are not identified, per the responsible disclosure agreement.

The scan, run in parallel — one of us focused on the networking classes, the other on the configuration classes — quickly converged on a single method responsible for mapping environment (production, pre-production, distinct regions) to the analytics server URL and its corresponding app key.

In that method, production keys and test-environment keys were concentrated side by side, with no segregation whatsoever. This is a recurring pattern in enterprise apps: since multiple environments need to coexist in the same binary for internal builds, it's common to find entire configuration maps — including secrets — hardcoded in a single "config" class.

---

## Phase 2: The Key Becomes a Door

With a valid production app key in hand, the next step was to precisely map what it authorized on the server. Two behaviors of the SDK's API proved problematic, as neither required any additional authentication layer:

**a) Remote config read access**

```
GET /o/sdk?method=fetch_remote_config&app_key=<REDACTED>&device_id=<arbitrary>
```

The endpoint returned, for any client presenting the app key, the feature flags and A/B testing parameters configured for the app — experiment names, control groups, and active variants. In other words: information about what the company is testing internally before rolling it out to all users, visible to anyone who has extracted the key from the APK.

**b) Arbitrary event injection (data poisoning)**

```
POST /i?app_key=<REDACTED>&device_id=<arbitrary_forged_id>
Content-Type: application/x-www-form-urlencoded

events=[{"key":"custom_event","count":1}]
```

The event ingestion endpoint accepted, with no origin validation whatsoever, forged sessions and custom events tied to an arbitrary device_id. This means an attacker could inject an artificial volume of fake events, contaminating the metrics the product team relies on for decision-making — from small statistical distortions to the complete invalidation of an A/B test, depending on the scale of the attack.

> **💡 Red Team Tradecraft:** the critical point is that both capabilities depended exclusively on a fixed string, identical across every install of the app, and fully extractable with free, publicly available tools. There was no second factor. There was no friction. Just the key and the door.

---

## Impact

From a risk perspective, it's worth separating technical impact from business impact:

- **Internal roadmap confidentiality** — experiment names, control groups, and feature flags aren't "secrets" in the personal-data sense, but they reveal product strategy normally restricted to internal teams.
- **Analytics data integrity** — the ability to inject fake events undermines the reliability of metrics used for product decisions. A motivated attacker could, in theory, manipulate the outcome of an A/B test by forging event volume toward a specific variant.
- **Expanded attack surface** — the same hardcoded-key pattern repeated across multiple environments and regions, all exposed in the same binary — this wasn't an isolated leak, but a systemic configuration practice.

Validation testing was conducted against the **production environment**, but restricted to fictitious device_ids and isolated test events — no real user data was accessed or altered, in compliance with the program's rules.

---

## Detection & Mitigation (Blue Team Perspective)

- **Never hardcode long-lived secrets in the client.** Even "low-risk" app keys should be treated as secrets: any publicly distributed binary is, by definition, code an attacker can read.
- **Prefer dynamic credential provisioning.** The key should be obtained at runtime, after user authentication, via a backend endpoint controlled by the company itself — never statically embedded in the APK.
- **Treat "internal environments" as attack surface.** Pre-production builds often receive less security attention than production, but since they ship in the same distributed binary, they end up exposed the same way — and in this case, it was the production key that turned out to be exploitable.
- **Add origin validation on server-side endpoints.** Certificate pinning, app signature verification, and rate limiting on ingestion and read endpoints drastically reduce abuse, even if a key leaks.
- **Have a credential rotation plan.** If a hardcoded key is discovered, the correct response is immediate rotation — keeping old keys valid after disclosure only extends the exposure window.
- **Audit your own binary the way an attacker would.** Running apktool and grepping for hash/token patterns on your own APK before release is a cheap check and should be part of the CI/CD pipeline for mobile apps.

---

## Indicators of Compromise (IOCs)

- **Network:** requests to analytics SDK endpoints with a fixed `app_key` coming from multiple origins/IPs not matching the official app.
- **Abuse pattern:** anomalous volume of custom events with sequential or clearly forged `device_id`s.
- **Binary:** presence of environment→credential configuration maps concentrated in a single config class in the APK.

---

## Behind the Hunt

This finding emerged from a broader recon process focused specifically on this app. The initial motivation was simply to map which third-party SDKs the app loaded — and the analytics SDK stood out precisely because it's less common than options like Firebase Analytics, which historically means less public scrutiny of its client-side implementations.

Working as a pair changed the pace of the investigation. While one of us kept mapping the configuration classes in smali, the other validated hypotheses directly against the API, testing authentication boundaries and cataloging which endpoints actually accepted the key with no additional verification. Having two people questioning the same hypothesis avoids the classic solo bug-hunting mistake: convincing yourself a behavior is "just that" when it's actually the tip of a larger chain.

A practical lesson for anyone getting started in mobile bug bounty: analytics/telemetry libraries deserve to be treated as a review priority, not as noise. They tend to carry "low-risk" credentials in the mind of whoever implements them — and precisely because of that, they end up less protected than user authentication tokens, even when their abuse has real impact, and even when the key that opens is the production one.

The report was submitted to the program and classified as **P2** by the responsible team — a high severity rating, reflecting the actual reach of the flaw: a single string, with no authentication layer whatsoever, controlling read access to internal configuration and the integrity of analytics data in production.

---

## Conclusion

This case is a direct example of how a seemingly harmless engineering practice — embedding a configuration key in the app — can turn into a real chain of vulnerabilities when the endpoint on the other side enforces no additional authentication layer. The fix is conceptually simple (don't fix secrets in the client, validate origin server-side), but requires process discipline to avoid reappearing in future builds.

And, as far as we're concerned, we keep hunting this kind of pattern together.

> **⚠️ Disclaimer:** This research was conducted within the authorized scope of a private bug bounty program. Company names, app names, files, and original keys have been omitted or generalized in this public version as a matter of responsible disclosure best practice.

---
