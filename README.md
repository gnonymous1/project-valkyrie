# PROJECT VALKYRIE
**Autonomous Wireless Interdiction Swarm**

Project Valkyrie is an advanced, cognitive Wi-Fi security assessment agent designed for Kali Linux. It leverages AI (Gemini) to perform intelligent, context-aware wireless audits and attacks.

## Features
*   **Autonomous Swarm**: coordinated agents for Recon, Threat Modeling, and Exploitation.
*   **Lethal Capabilities**:
    *   **WPS**: Pixie Dust & PIN Brute-force (`reaver`, `bully`).
    *   **PMKID**: Client-less capture (`hcxdumptool`).
    *   **Handshake**: Deauthentication & Capture (`aireplay-ng`).
*   **Cognitive Engine**: Uses Gemini AI to analyze targets and suggest vulnerabilities based on vendor/encryption.
*   **Professional TUI**: A "Hacker Movie" style terminal interface with live dashboards.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/rjy2915/project-valkyrie.git
    cd project-valkyrie
    ```

2.  **Make scripts executable** (Critical Step):
    ```bash
    chmod +x install.sh run.sh
    ```

3.  Install Dependencies:
    ```bash
    sudo ./install.sh
    ```


## Usage

**Basic Run:**
```bash
sudo ./run.sh
```

**With AI Capabilities:**
1.  Get an API Key from [Google AI Studio](https://aistudio.google.com/).
2.  Export it:
    ```bash
    export GEMINI_API_KEY="your_api_key_here"
    ```
3.  Run with `-E` to preserve the environment variable:
    ```bash
    sudo -E ./run.sh
    ```

## Interface Controls
*   `Arrow Keys`: Navigate lists.
*   `A`: Request AI Analysis for selected target.
*   `D`: Toggle Dry Run mode.
*   `Q`: Quit.

## Disclaimer
This tool is for educational purposes and authorized security assessments only. Use responsibly.
