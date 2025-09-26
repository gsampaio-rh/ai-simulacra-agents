#!/usr/bin/env python3
"""Main entry point for AI Simulacra Agents simulation."""

import asyncio
import logging
import sys
from pathlib import Path

# Add src to path so we can import simulacra
sys.path.insert(0, str(Path(__file__).parent / "src"))

from simulacra.cli.main import cli


def setup_logging():
    """Setup logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point."""
    setup_logging()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        print("🤖 AI Simulacra Agents")
        print("=" * 30)
        print()
        print("Usage:")
        print("  python main.py <command>")
        print()
        print("Commands:")
        print("  start        - Start the simulation")
        print("  step         - Advance by one tick")
        print("  status       - Show simulation status")
        print("  agent <id>   - Show agent details & memories")
        print("  export       - Export data for analysis")
        print("  interactive  - Start interactive mode")
        print()
        print("Examples:")
        print("  python main.py status")
        print("  python main.py step")
        print("  python main.py agent isabella")
        print("  python main.py agent isabella --query 'social interactions'")
        print("  python main.py export")
        print("  python main.py interactive")
        print()
        return
    
    # Run the CLI
    cli()


if __name__ == "__main__":
    main()
