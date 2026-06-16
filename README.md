<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a0a,40:1a0000,100:3d0000&height=220&section=header&text=Project%20Valkyrie&fontSize=56&fontColor=ff4444&fontAlignY=36&desc=Autonomous%20AI-Cognitive%20Wireless%20Security%20Assessment%20Agent%20%7C%20Kali%20Linux&descSize=16&descAlignY=58&animation=fadeIn" width="100%"/>

<br/>

[![Version](https://img.shields.io/badge/Status-Operational-ef4444?style=for-the-badge&labelColor=0a0a0a)](https://github.com/gnonymous1/project-valkyrie)
[![Platform](https://img.shields.io/badge/Platform-Kali%20Linux-557C94?style=for-the-badge&logo=kalilinux&logoColor=white&labelColor=0a0a0a)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white&labelColor=0a0a0a)](#)
[![License](https://img.shields.io/badge/License-MIT-10b981?style=for-the-badge&labelColor=0a0a0a)](LICENSE)
[![PRs](https://img.shields.io/badge/PRs-Welcome-f59e0b?style=for-the-badge&labelColor=0a0a0a)](CONTRIBUTING.md)

[![Gemini AI](https://img.shields.io/badge/Gemini%20AI-Cognitive%20Engine-4285F4?style=for-the-badge&logo=google&logoColor=white&labelColor=0a0a0a)](#)
[![Aircrack](https://img.shields.io/badge/Aircrack--ng-Suite-ef4444?style=for-the-badge&labelColor=0a0a0a)](#)
[![WPS](https://img.shields.io/badge/WPS%20Attack-Reaver%20%7C%20Bully-f97316?style=for-the-badge&labelColor=0a0a0a)](#)
[![PMKID](https://img.shields.io/badge/PMKID-hcxdumptool-7c3aed?style=for-the-badge&labelColor=0a0a0a)](#)

<br/>

> **Recon. Model. Strike.**
> An autonomous AI-cognitive wireless security agent with swarm coordination, Gemini-powered target analysis, and a professional hacker-movie TUI.

</div>

---

## 🔍 What Is Project Valkyrie?

**Project Valkyrie** is an advanced, autonomous Wi-Fi security assessment framework for Kali Linux. It leverages **Google Gemini AI** as a cognitive reasoning engine to perform intelligent, context-aware wireless audits — selecting attack vectors based on vendor fingerprinting, encryption type, and network configuration.

Designed for **authorized penetration testers and wireless security researchers** who need more than raw tools — they need **intelligent coordination**.

```
[Wireless Environment]
        │
        ▼
┌─────────────────────────────────────────────────────┐
│                VALKYRIE SWARM                        │
│                                                     │
│  🔭  Recon Agent      →  AP discovery, BSSID enum  │
│  🧠  Threat Model     →  Gemini AI analysis        │
│  ⚔️   Exploit Agent   →  WPS / PMKID / Handshake   │
│                                                     │
│  Coordination: autonomous agent mesh                │
│  Interface: Professional hacker-movie TUI           │
└─────────────────────────────────────────────────────┘
        │
        ▼
[Captured Credentials / Hash / Audit Report]
```

---

## ⚡ Capability Matrix

<div align="center">

| Attack Vector | Tool | Status |
|:------------:|:----:|:------:|
| **WPS Pixie Dust** | `reaver` + `bully` | ✅ Fully Implemented |
| **WPS PIN Brute-force** | `reaver` + `bully` | ✅ Fully Implemented |
| **PMKID Capture** | `hcxdumptool` | ✅ Fully Implemented |
| **Handshake Deauth** | `aireplay-ng` + `airodump-ng` | ✅ Fully Implemented |
| **Real-time AP Discovery** | `airodump-ng` | ✅ Fully Implemented |
| **WPS Detection** | `wash` | ✅ Fully Implemented |
| **AI Target Analysis** | Gemini API | ✅ Cognitive Engine |
| **Monitor Mode Auto** | `airmon-ng` | ✅ Auto-verified |

</div>

---

## ⚡ Quick Start

### Prerequisites

```
Kali Linux (recommended)  •  Python 3.10+  •  aircrack-ng suite
reaver  •  bully  •  hcxdumptool  •  root/sudo
WiFi adapter with monitor mode support
```

### 1 — Clone & Install

```bash
git clone https://github.com/gnonymous1/project-valkyrie.git
cd project-valkyrie

chmod +x install.sh run.sh
sudo ./install.sh
```

### 2 — Configure Gemini AI (Optional — for cognitive analysis)

```bash
cp .env.example .env
# Add your Gemini API key to .env:
# GEMINI_API_KEY=your_key_here
```

Get a free key at [aistudio.google.com](https://aistudio.google.com/).

> 🔐 Key is read from environment variable only — never hardcode it.

### 3 — Launch

```bash
# Standard launch
sudo ./run.sh

# Custom wireless interface
sudo ./run.sh --interface wlan1

# With AI capabilities (reads GEMINI_API_KEY from .env)
sudo ./run.sh

# Dry run / simulation mode (no real attacks)
sudo ./run.sh --dry-run

# Enhanced mode
sudo ./run_enhanced.sh
```

---

## 🖥️ Terminal Interface Controls

```
┌─────────────────────────────────────────────────────────────┐
│                  VALKYRIE COMMAND INTERFACE                  │
│                                                             │
│   ↑ ↓     Navigate target list                             │
│   A        Request Gemini AI analysis for selected target   │
│   D        Toggle dry-run (simulation) mode                 │
│   Q        Quit and cleanup                                 │
│                                                             │
│   Live Dashboard: AP list · RSSI · Encryption · WPS state  │
│   Status Panel:  Agent state · Attack progress · Findings   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧠 Gemini AI Cognitive Engine

When a Gemini API key is configured, Valkyrie activates its cognitive reasoning layer:

- **Vendor Fingerprinting** — identifies router manufacturer from BSSID OUI
- **Encryption Analysis** — scores attack feasibility (WPA2/WPA3/WEP)
- **Vulnerability Suggestions** — recommends optimal attack vectors
- **Risk Assessment** — context-aware threat modeling per target

```bash
# Configure in .env
GEMINI_API_KEY=your_api_key_here

# Or export directly (not recommended for production)
export GEMINI_API_KEY="your_key"
sudo -E ./run.sh   # -E preserves environment
```

---

## 📁 Project Structure

```
project-valkyrie/
│
├── 🧠  agents/               Autonomous swarm agents
│   ├── recon_agent.py       AP discovery & enumeration
│   ├── threat_model.py      Gemini AI cognitive analysis
│   └── exploit_agent.py     Attack execution coordinator
│
├── ⚙️   core/                Core framework
│   ├── monitor.py           Monitor mode management
│   ├── scanner.py           Network scanning engine
│   └── capture.py           Handshake/PMKID capture
│
├── 🖥️   ui/                  Terminal UI
│   └── tui.py               Hacker-movie style dashboard
│
├── 📋  requirements.txt      Python dependencies
├── 🔧  install.sh            Dependency installer
├── 🚀  run.sh                Standard launcher
├── 🚀  run_enhanced.sh       Enhanced mode launcher
└── 🔐  .env.example          API key template
```

---

## 🛡️ Technical Highlights

- **Real Tool Integration** — all wireless tools (reaver, aircrack-ng, hcxdumptool) fully integrated, not mocked
- **Automatic Monitor Mode** — activates and verifies monitor mode on launch
- **Real Scanning** — airodump-ng CSV parsing for live AP discovery
- **WPS Detection** — `wash` integration for WPS-enabled network identification
- **Full Handshake Flow** — complete deauth + capture + verify workflow
- **PMKID Extraction** — complete extraction with hash verification
- **Proper Cleanup** — exception handling and interface restoration on exit

---

## 🗺️ Roadmap

- [ ] Hashcat integration for offline hash cracking
- [ ] PMKID → hashcat pipeline automation
- [ ] WPA3 SAE (Dragonblood) assessment module
- [ ] Multi-adapter swarm deployment
- [ ] Web-based reporting dashboard
- [ ] Plugin API for custom attack modules

---

## ⚖️ Legal & Ethics

**Project Valkyrie is strictly for authorized security assessment only.**

- You **must** have explicit written permission to audit any wireless network
- Unauthorized use is **illegal** in most jurisdictions
- This tool is designed for penetration testers, security researchers, and CTF players working within authorized scope
- The developer assumes **zero liability** for misuse

---

## 🤝 Contributing

```bash
git checkout -b feature/your-module
# Build, test on authorized hardware
git commit -m "feat: your module"
# Open a Pull Request
```

---

<div align="center">

[![Stars](https://img.shields.io/github/stars/gnonymous1/project-valkyrie?style=social)](https://github.com/gnonymous1/project-valkyrie/stargazers)
[![Forks](https://img.shields.io/github/forks/gnonymous1/project-valkyrie?style=social)](https://github.com/gnonymous1/project-valkyrie/network/members)

[🐛 Report Bug](https://github.com/gnonymous1/project-valkyrie/issues/new) • [✨ Request Feature](https://github.com/gnonymous1/project-valkyrie/issues/new)

<br/>

*Valkyrie — Cognitive Wireless Interdiction.*

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:3d0000,50:1a0000,100:0a0a0a&height=100&section=footer" width="100%"/>

</div>
