"""
Command-line interface for NeuroGraph Jupyter integration.
"""

import sys
import argparse


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="NeuroGraph Jupyter Integration CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Load the extension in Jupyter
  %load_ext neurograph_jupyter

  # Initialize NeuroGraph
  %neurograph init --path ./my_graph.db

  # Query the graph
  %neurograph query "find all nodes"

  # Check status
  %neurograph status

For more information, visit:
  https://github.com/chrnv/neurograph-os-mvp
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version='neurograph-jupyter 0.63.1'
    )

    parser.add_argument(
        'command',
        nargs='?',
        choices=['info', 'help'],
        default='help',
        help='Command to execute'
    )

    args = parser.parse_args()

    if args.command == 'info' or args.command == 'help':
        print("NeuroGraph Jupyter Integration v0.63.1")
        print()
        print("To use in Jupyter notebooks:")
        print("  %load_ext neurograph_jupyter")
        print()
        print("Available magic commands:")
        print("  %neurograph init --path <db_path>  - Initialize connection")
        print("  %neurograph status                 - Show system status")
        print("  %neurograph query <query>          - Execute query")
        print("  %neurograph subscribe <channel>    - Subscribe to channel")
        print("  %neurograph emit <channel> <data>  - Emit event")
        print()
        print("For full documentation, see:")
        print("  https://github.com/chrnv/neurograph-os-mvp/blob/main/README.md")
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main())
