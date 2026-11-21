# Project Glasswing / Claude Mythos fact-check

**Research snapshot:** 21 November 2026. This file distinguishes Anthropic's own programme reporting from independently audited facts. The dialogue deliberately avoids saying that Mythos literally saved the internet.

## Supported statements used in the script

| Script point | What the source says | Safe wording in the video |
|---|---|---|
| Launch date and purpose | Anthropic announced Project Glasswing on 7 April 2026 as a defensive initiative using Claude Mythos Preview to help secure critical software. | “Anthropic announced it on April seventh, twenty twenty-six…” |
| Initial partners | The launch group included AWS, Anthropic, Apple, Broadcom, Cisco, CrowdStrike, Google, JPMorganChase, the Linux Foundation, Microsoft, NVIDIA and Palo Alto Networks. Anthropic also described more than 40 additional organisations with access. | “The first partners included major cloud, chip, software and security companies…” |
| OpenBSD example | Anthropic says Mythos found a 27-year-old OpenBSD vulnerability that could let an attacker remotely crash a machine by connecting to it. Anthropic says it was reported to maintainers and patched. | State this as an example Anthropic reported, not as an independently reproduced test in this video. |
| FFmpeg example | Anthropic says it found a 16-year-old FFmpeg vulnerability in code that automated testing tools had exercised five million times without catching the flaw. | “The relevant code had been exercised around five million times.” |
| Linux example | Anthropic says it autonomously chained several Linux kernel vulnerabilities to escalate from ordinary user access to full control. | Describe the high-level outcome only; do not show an operational exploit or reproduction instructions. |
| More than 10,000 findings | On 22 May 2026, Anthropic reported that it and approximately 50 partners had found more than 10,000 high- or critical-severity vulnerabilities. | Explicitly attribute the figure to Anthropic; do not frame it as an independent audit. |
| Expansion | On 2 June 2026, Anthropic said it was extending access to approximately 150 new organisations across more than 15 countries, including power, water, healthcare, communications and hardware. | Attribute this access expansion to Anthropic. |
| Bottleneck shift | Anthropic's 22 May update says discovery had become faster and that verification, disclosure and patching were now the bottleneck. | Present this as Anthropic's assessment and an argument for George to scrutinise. |

## Important caveats retained in the dialogue

- 10,000+ is a reported programme total from Anthropic, not independently audited by this production.
- The video is not a security audit and does not reproduce, verify or demonstrate the vulnerabilities.
- Discovering a vulnerability is not the same as patching it; patching is not the same as deployment; deployment is not the same as proof that every exposed system is protected.
- The debate's three speakers are fictional roles, not real Anthropic staff, security researchers, partner spokespeople or maintainers. Their dialogue is original and must never be presented as a real quotation.
- “Saved the internet” is a provocative question, not a factual conclusion. The final answer is deliberately qualified: Project Glasswing helped selected defenders see and investigate weaknesses; lasting protection depends on responsible fixes, deployment and sustained maintenance.

## Primary sources

1. Anthropic, Project Glasswing, announced 7 April 2026: https://www.anthropic.com/project/glasswing
2. Anthropic, Project Glasswing: Securing critical software for the AI era: https://www.anthropic.com/glasswing
3. Anthropic, Project Glasswing: An initial update, published 22 May 2026: https://www.anthropic.com/news/glasswing-initial-update
4. Anthropic, Expanding Project Glasswing, published 2 June 2026: https://www.anthropic.com/news/expanding-project-glasswing

## Voice implementation references

- Kyutai Pocket TTS Python API: https://kyutai-labs.github.io/pocket-tts/API%20Reference/python-api/
- Kyutai Pocket TTS overview and CPU support: https://kyutai-labs.github.io/pocket-tts/
- Kokoro voice roster (includes am_liam): https://huggingface.co/Codobo/Kokoro-82M/blob/main/VOICES.md

## Review rule

Before publication, re-open the primary sources and ensure no programme total, date, sector list, vulnerability age or severity claim has changed. Update this file and the script together if the factual source changes.