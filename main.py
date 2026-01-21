import argparse
import sys
import logging
from core.security_checks import SecurityChecks
from ui.enhanced_app import EnhancedWifiAgentApp

def setup_logging():
    """Setup application logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('valkyrie.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    setup_logging()
    logger = logging.getLogger(__name__)
    
    parser = argparse.ArgumentParser(description="PROJECT VALKYRIE: Autonomous Wireless Interdiction Swarm")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without hardware access")
    parser.add_argument("--interface", type=str, default="wlan0", help="Wireless interface to use")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Perform security checks before launching
    if not args.dry_run:
        logger.info("Performing preflight security checks...")
        issues = SecurityChecks.perform_preflight_checks(args.interface)
        
        if issues:
            logger.error("Preflight checks failed:")
            for issue in issues:
                print(f"  - {issue}")
            sys.exit(1)
        else:
            logger.info("All preflight checks passed")
    
    # Launch Textual App
    try:
        app = EnhancedWifiAgentApp(dry_run=args.dry_run, interface=args.interface)
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
