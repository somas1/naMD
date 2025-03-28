#!/usr/bin/env python3.12
# load_env_vars.py

"""Loads the secret Tailscale Auth Key interactively for shell use.

Checks if TS_AUTHKEY is already set in the environment. If not found,
prompts the user to enter it securely (input is hidden). Outputs an `export`
command to stdout for use with `eval` in the shell.

All other non-secret, project-specific configurations (like TS_HOSTNAME,
TS_SERVE_CONFIG_JSON, TS_EXTRA_ARGS, TS_FUNNEL_ENABLE) MUST be set directly
in the `environment:` section of the `tailscale` service within your project's
`docker-compose.override.yaml` file. This script does NOT handle those.

Usage:
  eval $(python3.12 load_env_vars.py)

Then run docker compose:
  docker compose up -d
"""

import os
import sys
import getpass
from typing import Dict, Optional, List, Any

# --- Configuration ---
# ONLY handle the secret Auth Key here.
REQUIRED_VARS: Dict[str, Dict[str, Any]] = {
    'TS_AUTHKEY': {
        'secret': True,
        'prompt': 'Enter your Tailscale Auth Key',
        'required': True,
    }
    # Other variables like TS_HOSTNAME, TS_SERVE_CONFIG_JSON, etc.,
    # MUST be defined in docker-compose.override.yaml
}

# Set to True to always output export command even if TS_AUTHKEY is already set
EXPORT_EXISTING_VARS: bool = False


def get_variable_value(var_name: str, config: Dict[str, Any]) -> Optional[str]:
    """Retrieves the value for the TS_AUTHKEY, prompting if needed.

    Checks `os.getenv` for the variable. If found, returns it immediately unless
    EXPORT_EXISTING_VARS is True. If not found or export is forced, prompts
    the user based on the provided configuration dictionary using `getpass.getpass()`.

    Args:
        var_name: The name of the environment variable (should be 'TS_AUTHKEY').
        config: Configuration dictionary for the variable.

    Returns:
        The value of the environment variable (str) if found or entered.
        Returns None if the variable is required and the user provides no input.

    Raises:
        EOFError: If the user cancels input via Ctrl+D.
        KeyboardInterrupt: If the user cancels input via Ctrl+C.
    """
    value = os.getenv(var_name)
    prompt_required = False

    if value and not EXPORT_EXISTING_VARS:
        print(f"- {var_name}: Found in environment.", file=sys.stderr)
        return value # Already set, no need to prompt or export
    elif value and EXPORT_EXISTING_VARS:
         print(f"- {var_name}: Found in environment (exporting anyway).", file=sys.stderr)
         prompt_required = True # Treat as if prompting was needed to ensure it gets exported
         # We will re-use the existing value below if no new input is given (though prompt occurs)
    else:
        prompt_required = True
        print(f"- {var_name}: Not found. Prompting...", file=sys.stderr)

    if prompt_required:
        try:
            prompt_message = f"  {config.get('prompt', f'Enter value for {var_name}')}: "
            if config.get('secret', False): # Should always be true for TS_AUTHKEY
                entered_value = getpass.getpass(prompt_message)
            else: # Fallback, but shouldn't be used for TS_AUTHKEY
                entered_value = input(prompt_message)

            # If user just hits enter on prompt for existing var being re-exported, use original
            if not entered_value and value and EXPORT_EXISTING_VARS:
                return value

            # If no value entered (and wasn't pre-existing) check if required
            if not entered_value:
                if config.get('required', True): # Should always be true for TS_AUTHKEY
                    print(f"  Error: A value is required for {var_name}.", file=sys.stderr)
                    return None # Signal that a required value was missing
                # else: # Not applicable for TS_AUTHKEY
                #     return ""

            return entered_value # Return the newly entered value

        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled by user.", file=sys.stderr)
            # Reraise to allow the main loop to handle exit
            raise
    # This part should ideally not be reached if EXPORT_EXISTING_VARS logic is correct
    return value


def generate_export_command(var_name: str, value: str) -> Optional[str]:
    """Generates a shell 'export' command string, safely quoting the value.

    Formats the string as `export VAR_NAME='value'`. Includes a basic safety
    check to prevent command injection issues if the value contains single quotes.

    Args:
        var_name: The name of the environment variable.
        value: The value to assign to the variable.

    Returns:
        The formatted `export` command string (e.g., "export TS_AUTHKEY='...'").
        Returns None if the value contains characters deemed unsafe (single quotes).
    """
    if "'" in value:
        print(f"  Error: Value for {var_name} contains single quotes ('): \"{value[:20]}...\"", file=sys.stderr)
        print(f"  This cannot be safely handled by simple quoting for 'eval'.", file=sys.stderr)
        print(f"  Please set the variable manually in your shell or use a value without single quotes.", file=sys.stderr)
        return None
    return f"export {var_name}='{value}'"


def main() -> None:
    """Main function to check TS_AUTHKEY, prompt if needed, and generate export command."""
    print("Checking required secret environment variables...", file=sys.stderr)
    export_commands: List[str] = []
    all_vars_ok = True

    try:
        for var_name, config in REQUIRED_VARS.items(): # Will only loop for TS_AUTHKEY
            value = get_variable_value(var_name, config)

            if value is None and config.get('required', True):
                 all_vars_ok = False
                 print(f"Failed to get required value for {var_name}.", file=sys.stderr)
                 continue

            if value is not None:
                command = generate_export_command(var_name, value)
                if command:
                    export_commands.append(command)
                else:
                    all_vars_ok = False
                    print(f"Skipping export for {var_name} due to invalid characters.", file=sys.stderr)

    except (EOFError, KeyboardInterrupt):
        sys.exit(1)

    if not all_vars_ok:
        print("\nErrors encountered. Could not prepare secret variable for export.", file=sys.stderr)
        sys.exit(1)

    if export_commands:
        print("\nSecret variable(s) ready for export.", file=sys.stderr)
        print("If using 'eval', run:", file=sys.stderr)
        python_executable = sys.executable or f"python{sys.version_info.major}.{sys.version_info.minor}"
        script_path = os.path.abspath(__file__)
        print(f"eval $({python_executable} {script_path})\n", file=sys.stderr)
        print('\n'.join(export_commands)) # Print export command(s) to stdout
    else:
        print("\nNo export commands generated for secrets (TS_AUTHKEY may already be set).", file=sys.stderr)


if __name__ == "__main__":
    main()