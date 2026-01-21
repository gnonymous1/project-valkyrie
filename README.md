# PROJECT VALKYRIE
**Autonomous Wireless Interdiction Swarm**

Project Valkyrie is an advanced, cognitive Wi-Fi security assessment agent designed for Kali Linux. It leverages AI (Gemini) to perform intelligent, context-aware wireless audits and attacks.

## Features
*   **Autonomous Swarm**: coordinated agents for Recon, Threat Modeling, and Exploitation.
*   **Lethal Capabilities**:
    *   **WPS**: Pixie Dust & PIN Brute-force (`reaver`, `bully`) - FULLY IMPLEMENTED.
    *   **PMKID**: Client-less capture (`hcxdumptool`) - FULLY IMPLEMENTED.
    *   **Handshake**: Deauthentication & Capture (`aireplay-ng`, `airodump-ng`) - FULLY IMPLEMENTED.
    *   **Network Scanning**: Real-time AP discovery using `airodump-ng` - FULLY IMPLEMENTED.
*   **Cognitive Engine**: Uses Gemini AI to analyze targets and suggest vulnerabilities based on vendor/encryption.
*   **Professional TUI**: A "Hacker Movie" style terminal interface with live dashboards.
*   **Real Tool Integration**: All wireless tools are now properly integrated instead of mocked.

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

**With Custom Interface:**
```bash
sudo ./run.sh --interface wlan1
```

**Dry Run Mode (Simulation):**
```bash
sudo ./run.sh --dry-run
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

## Technical Improvements
*   **Real Tool Integration**: All wireless tools (reaver, aircrack-ng suite, hcxdumptool) are now fully integrated instead of mocked
*   **Proper Monitor Mode**: Automatic monitor mode activation with verification
*   **Real Scanning**: Network discovery through airodump-ng with CSV parsing
*   **WPS Detection**: Wash integration for WPS-enabled network detection
*   **Handshake Capture**: Full implementation of deauth + handshake capture workflow
*   **PMKID Capture**: Complete PMKID extraction with hash verification
*   **Error Handling**: Proper exception handling and cleanup routines

## Disclaimer
This tool is for educational purposes and authorized security assessments only. Use responsibly.
