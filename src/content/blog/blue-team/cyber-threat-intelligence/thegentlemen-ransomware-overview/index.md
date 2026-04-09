---
title: "TheGentlemen Ransomware: Threat Overview and Analysis"
description: "Technical overview of TheGentlemen ransomware group, covering its operational model, TTPs, initial access vectors, and defensive considerations."
risk: "INFO"
pubDate: 2026-04-07
author: "ANKHCORP"
team: "Blue Team"
category: "Cyber Threat Intelligence"
tags: ["Ransomware", "Threat Intelligence", "Cybersecurity", "TTPs", "Blue Team", "Malware"]
---

## Threat Context

**The Gentlemen** is a ransomware group that carries out numerous attacks around the world and has recently attracted notable attention, especially due to the concentration of victims in countries with lower cybersecurity maturity.

They remain active, with their first appearance around mid-2025.

**Primary Nation Targets:**

US, Brazil, Thailand and India

**Primary Industry Targets:**

Logistics, Manufacturing, Financial Services, and Healthcare

**First Known Victim:**
JN Aceros (Peru) on 06/30/2025

![The Gentleman DLS PHOTO](Image-1.png)

The core of **TheGentlemen** is a system of unique keys generated for each victim at the time of the attack.

Each file is encrypted with its own key, created temporarily during the process. This key is then protected using a public key controlled by the criminal group and appended to the end of the file.

Without the corresponding private key, which remains only on the attackers’ servers, it is not possible to recover the files. The decryptor they provide after payment already contains this private key hidden and obfuscated within the program itself. That is why it can operate offline and across different systems. It simply extracts the key and uses the information stored in the files to reverse the encryption.

The group follows a **double extortion** model. Data is exfiltrated from the victim’s servers before encryption begins, and if the ransom is not paid, the data will still be published on the group’s Darknet site.

![Affiliate Program Post](Image-2.png)

## Encryption Model & Affiliate Program

The group’s core infrastructure operates through DLS and TOX. They follow the classic Ransomware-as-a-Service model, where developers create the malware and affiliates carry out the attacks. They prohibit members residing in Russia and CIS countries from participating in the group.

CIS stands for the Commonwealth of Independent States, formed by some countries that were part of the former Soviet Union, such as Belarus, Kazakhstan, Armenia, Kyrgyzstan, among others.

The group targets a wide range of systems, including Windows, Linux and BSD, NAS devices, and ESXi virtualization environments.

Although the group has targeted some specific niches in recent months, this does not indicate a fixed focus on any particular industry. They are capable of attacking medium and large companies, hospitals, industries, service providers, and more. They maintain a strong online presence and use an aggressive extortion approach, making them one of the leading ransomware groups today.

![Affiliate Program Post](Image-3.png)

They require individuals interested in joining the group to justify their application and make a deposit of $1,500. According to the group, this amount will be refunded after the first successful payment. According to the announcement, the measure is intended to filter out researchers and law enforcement agents. This recruitment mechanism acts as a barrier to entry and demonstrates a strong concern for OPSEC.

Like most ransomware groups, they use Tox and Session for communication.

![Note](Note.png)

## TTPs

**Initial Access:**

T1190 (Exploit Public-Facing Application) using FortiGate and FortiOS (CVE-2024-55591)
T1110 (Brute Force: Password Guessing)
VPNs and administrative panels
Use of compromised credentials (VPN and admin)

**Recon:**

Advanced IP Scanner
Full network mapping prior to execution

**Defense Evasion:**

BYOVD (Bring Your Own Vulnerable Driver) using CVE-2025-7771
Use of legitimate vulnerable drivers, for example ThrottleBlood.sys
EDR and AV termination at the kernel level

**Lateral Movement:**

Use of legitimate administrative tools such as PsExec and internal tools following the LOLBins pattern, inferred and commonly observed in campaigns
Complex Active Directory environments

## IoCs (Indicators of Compromise):

Identified strings: “Ransom Protection(DON’T DELETE)”

**Known samples (SHA256):**

3ab9575225e00a83a4ac2b534da5a710bdcf6eb72884944c437b5fbe5c5c9235
51b9f246d6da85631131fcd1fabf0a67937d4bdde33625a44f7ee6a3a7baebd2 

**Tools and Binaries:**

All.exe, ThrottleBlood.sys, Allpatch2.exe

**Preventive Recommendations:**

Apply patches immediately to FortiGate and FortiOS
Disable exposed administrative access over the internet
Enforce MFA on VPNs and administrative panels
Rotate privileged credentials periodically
Monitor anomalous logins based on geography, time, and volume