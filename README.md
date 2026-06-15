```
 ██████╗ ██╗  ██╗██████╗ ██████╗ ██╗  ████████╗ █████╗
██╔═████╗╚██╗██╔╝██╔══██╗╚════██╗██║  ╚══██╔══╝██╔══██╗
██║██╔██║ ╚███╔╝ ██║  ██║ █████╔╝██║     ██║   ███████║
████╔╝██║ ██╔██╗ ██║  ██║ ╚═══██╗██║     ██║   ██╔══██║
╚██████╔╝██╔╝ ██╗██████╔╝██████╔╝███████╗██║   ██║  ██║
 ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═════╝ ╚══════╝╚═╝   ╚═╝  ╚═╝
```

# 0xDelta Research

**Offensive & defensive security research collective.**
Public intelligence archive at **[0xdelta.org](https://0xdelta.org)**.

`static` · `no-tracking` · `no-marketing` · `no-filler`

---

we are a closed group of offensive and defensive security practitioners.
we don't do marketing. we don't do certifications.
we work in the environments where attacks happen for real.

this repository is the source code for **[0xdelta.org](https://0xdelta.org)** — our public intelligence archive.
the site is open. the team is not.

---

## Mission

We dissect real-world threats and break real-world systems, then write down exactly how
and why — in the open. Every report on [0xdelta.org](https://0xdelta.org) is technical,
reproducible, and published only after it has been through the team.

If it's here, it went through the team. If it didn't, it's not here.

## Research Divisions

**🔴 Red Team — Offensive**
Offensive Techniques · Web Security · API Security · Network Security · Cloud Security ·
Active Directory · CVE Research · Bug Bounty

**🔵 Blue Team — Defensive**
Malware Analysis & Reverse Engineering · Threat Hunting · Detection Engineering ·
Cyber Threat Intelligence · OSINT · Privacy & Compliance

## Featured Research

| Report | Division | Author |
|--------|----------|--------|
| [UpCrypter Loader Delivering XWorm V5.6 RAT](https://0xdelta.org/blog/blue-team/malware-analysis-reverse-engineering/xworm-ucrypter-rat/) — full-chain analysis & config extraction | Malware Analysis | 0x_OLYMPUS |
| [EvilSoul1337 — Stealer-as-a-Service](https://0xdelta.org/blog/blue-team/malware-analysis-reverse-engineering/evilsoul1337/) | Malware Analysis | 0x_OLYMPUS |
| [Critical 10.0 — Full BI Infrastructure Compromise](https://0xdelta.org/blog/red-team/web-security/critical-microstrategy-default-creds/) | Web Security | SERROS404 |
| [TheGentlemen Ransomware — Threat Overview](https://0xdelta.org/blog/blue-team/cyber-threat-intelligence/thegentlemen-ransomware-overview/) | Threat Intel | ANKHCORP |
| [Critical IDOR in a PIX Payment Gateway](https://0xdelta.org/blog/blue-team/cyber-threat-intelligence/pix-gateway-idor/) | Threat Intel | 0x_OLYMPUS |
| [Threat Actor Profile: Midia22](https://0xdelta.org/blog/blue-team/threat-hunting/midia22/) | Threat Hunting | VAMPIR3BLUES |

> Full archive → **[0xdelta.org/blog](https://0xdelta.org/blog)**

## Automation & Intel Feeds

The team runs a set of autonomous bots (GitHub Actions) that watch the threat landscape
and push curated intel to our internal channels:

- **CVE Watcher + EPSS** — high-severity vulnerabilities, scored by exploitation probability
- **IOC Feed** — fresh indicators of compromise
- **Malware Monitor** — emerging samples and families
- **Ransomware Tracker** — active groups and victims
- **News Bot** — relevant cybersecurity developments

## Operators

| Operator | Division | Focus |
|----------|----------|-------|
| **[0x_OLYMPUS](https://www.linkedin.com/in/moises-cerqueira/)** | 🔵 Threat Research Lead | APT tracking, malware analysis, reverse engineering |
| **[SPECIEUNKN0WN_](https://github.com/stnert)** | 🔵 SOC Lead | Mobile security, data privacy, security operations |
| **[VAMPIR3BLUES](https://github.com/vampir3blues)** | 🔵 Threat Research | Cyber threat intelligence, threat hunting |
| **[SERROS404](https://github.com/serros404)** | 🔴 Red Team Lead | Web & API exploitation, bug bounty |
| **[ANKHCORP](https://github.com/Ankhcorp)** | 🔴 Red Team | Web exploitation, OSINT, C2 infrastructure |
| **[E0B3](https://github.com/Hunter-scriptkiddie)** | 🔴 Red Team | Bug hunting, recon methodology, tooling |
| **[RWX_GHOST](https://linkedin.com/in/rafael-henrique-cyber)** | 🔴 Red Team | Web, API & mobile bug hunting |

## Responsible Disclosure

Offensive research published here is conducted against systems we are authorized to test
or as part of coordinated, responsible disclosure. When we find a vulnerability in a
third-party product or service, we contact the affected party and allow remediation time
before publishing.

Reporting something to us, or affected by a report? → **root@0xdelta.org** (PGP below).

## Contact

```
github   → github.com/0xDelta-Research
linkedin → linkedin.com/company/0xdeltaresearch
web      → 0xdelta.org
contact  → root@0xdelta.org
```

**PGP** — sensitive intel and responsible disclosure must be encrypted.
Public key at [0xdelta.org/contact](https://0xdelta.org/contact).
Fingerprint: `29C7 138E 62E3 39CF CF67 E9FA B1D6 9660 A13D 37C2`

## Legal & Disclaimer

All content is provided **for educational and defensive purposes only**. Indicators,
samples, and techniques are published to help defenders detect and respond to real
threats. 0xDelta Research does not endorse, and is not responsible for, any misuse of the
information herein. Offensive findings are the result of authorized assessments or
responsible disclosure.

---

## About this repository

Source for [0xdelta.org](https://0xdelta.org) — a 100% static site.

**Stack:** Astro · React · Tailwind CSS · deployed on GitHub Pages.

```
// this repo accepts no external contributions
// the code is public because hiding it would be pointless
// 0x44 0x45 0x4C 0x54 0x41
```

> *"if you're looking for marketing-safe security, we're not it."*
