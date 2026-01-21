import argparse
import sys
from ui.app import WifiAgentApp

def main():
    parser = argparse.ArgumentParser(description="PROJECT VALKYRIE: Autonomous Wireless Interdiction Swarm")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without hardware access")
    parser.add_argument("--interface", type=str, default="wlan0", help="Wireless interface to use")
    args = parser.parse_args()

    # Launch Textual App
    app = WifiAgentApp(dry_run=args.dry_run, interface=args.interface)
    app.run()

if __name__ == "__main__":
    main()
