#!/usr/bin/env python3
"""
Platform Adapter - Handles OS-specific differences (Windows vs Unix).

Translates bash commands to PowerShell for Windows compatibility,
validates platform-specific command availability, and provides fallbacks.
"""

import platform
import os
import sys
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Platform(Enum):
    """Supported platforms."""
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


class PlatformAdapter:
    """Adapts commands and hooks to target platform."""

    # Command translations from bash to PowerShell
    BASH_TO_POWERSHELL = {
        "black": "python -m black",
        "prettier": "npx prettier",
        "rustfmt": "rustfmt",
        "gofmt": "gofmt -w",
        "git status": "git status",
        "git diff": "git diff",
        "git log": "git log",
        "git add": "git add",
        "git commit": "git commit",
        "git branch": "git branch",
        "git push": "git push",
        "git pull": "git pull",
        "pytest": "python -m pytest",
        "jest": "npm test",
        "npm test": "npm test",
        "cargo test": "cargo test",
        "go test": "go test ./...",
        "find": "Get-ChildItem -Recurse",
        "grep": "Select-String",
        "ls": "Get-ChildItem",
        "cat": "Get-Content",
        "mkdir": "New-Item -ItemType Directory",
        "rm": "Remove-Item",
        "cp": "Copy-Item",
        "mv": "Move-Item",
        "pwd": "Get-Location",
        "echo": "Write-Host"
    }

    # Tool availability checks per platform
    TOOL_CHECKS = {
        "Windows": {
            "black": "pip show black",
            "prettier": "npm list prettier",
            "rustfmt": "rustfmt --version",
            "git": "git --version",
            "python": "python --version",
            "npm": "npm --version",
            "cargo": "cargo --version"
        },
        "Unix": {
            "black": "command -v black",
            "prettier": "command -v prettier",
            "rustfmt": "command -v rustfmt",
            "git": "command -v git",
            "python": "command -v python3",
            "npm": "command -v npm",
            "cargo": "command -v cargo"
        }
    }

    def __init__(self):
        """Initialize platform adapter."""
        self.platform = self._detect_platform()
        self.is_windows = self.platform == Platform.WINDOWS
        self.is_unix = self.platform in [Platform.MACOS, Platform.LINUX]

    def _detect_platform(self) -> Platform:
        """Detect current operating system."""
        system = platform.system().lower()

        if system == "windows":
            return Platform.WINDOWS
        elif system == "darwin":
            return Platform.MACOS
        elif system == "linux":
            return Platform.LINUX
        else:
            return Platform.UNKNOWN

    def get_platform_name(self) -> str:
        """Get platform name."""
        return self.platform.value

    def translate_command(self, bash_command: str) -> Tuple[str, Optional[str]]:
        """
        Translate bash command to platform-appropriate form.

        Args:
            bash_command: Original bash command

        Returns:
            Tuple of (translated_command, warning_message)
        """
        if self.is_unix:
            return bash_command, None

        # For Windows, attempt translation
        command_lower = bash_command.lower().strip()

        # Check for exact matches
        if command_lower in self.BASH_TO_POWERSHELL:
            translated = self.BASH_TO_POWERSHELL[command_lower]
            warning = f"⚠️ Translated bash to PowerShell: {bash_command} → {translated}"
            return translated, warning

        # Check for partial matches (first word)
        first_word = command_lower.split()[0]
        if first_word in self.BASH_TO_POWERSHELL:
            # Build translated command with arguments
            args = bash_command[len(first_word):].strip()
            translated = self.BASH_TO_POWERSHELL[first_word]
            if args:
                translated = f"{translated} {args}"
            warning = f"⚠️ Translated bash command for Windows: {translated}"
            return translated, warning

        # Unable to translate
        warning = f"⚠️ Warning: Command '{bash_command}' may not work on Windows. Please verify."
        return bash_command, warning

    def create_platform_hook_command(self, bash_command: str) -> str:
        """
        Create platform-appropriate hook command.

        Args:
            bash_command: Original bash command

        Returns:
            Platform-appropriate hook command
        """
        if self.is_unix:
            # Use bash directly
            return f"bash -c '{self._escape_bash_quotes(bash_command)}'"
        else:
            # Use PowerShell
            translated, _ = self.translate_command(bash_command)
            escaped = translated.replace('"', '`"')
            return f'powershell -Command "{escaped}"'

    def validate_tool_availability(self, tool_name: str) -> Tuple[bool, str]:
        """
        Validate that a tool is available on this platform.

        Args:
            tool_name: Name of tool to check

        Returns:
            Tuple of (is_available, status_message)
        """
        platform_type = "Windows" if self.is_windows else "Unix"
        checks = self.TOOL_CHECKS.get(platform_type, {})

        if tool_name not in checks:
            return False, f"Unknown tool: {tool_name}"

        check_command = checks[tool_name]

        # On Windows, use where command
        if self.is_windows:
            check_cmd = f"where {tool_name} >nul 2>&1"
        else:
            check_cmd = check_command

        try:
            result = os.system(f"{check_cmd} 2>/dev/null")
            if result == 0:
                return True, f"✅ {tool_name} is available"
            else:
                return False, f"❌ {tool_name} not found. Install with: pip install {tool_name}"
        except Exception as e:
            return False, f"⚠️ Could not verify {tool_name}: {e}"

    def validate_hook_for_platform(self, hook_config: Dict) -> Tuple[bool, List[str]]:
        """
        Validate hook configuration for current platform.

        Args:
            hook_config: Hook configuration dict

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        # Get hook command
        hook_command = None
        if "hooks" in hook_config and len(hook_config["hooks"]) > 0:
            hook_command = hook_config["hooks"][0].get("command", "")

        if not hook_command:
            return False, ["No hook command found in configuration"]

        # Check for Windows-incompatible patterns
        if self.is_windows:
            incompatible_patterns = [
                "rm -rf",  # Dangerous on Windows too, but different
                "chmod",   # Unix permissions
                "sudo",    # Unix privilege elevation
                "/etc/",   # Unix paths
                "/usr/",   # Unix paths
                "$(",      # Bash command substitution
                "${",      # Bash variable expansion
                "|",       # Pipes may work differently
            ]

            for pattern in incompatible_patterns:
                if pattern in hook_command:
                    warnings.append(f"⚠️ Potentially incompatible pattern: '{pattern}'")

        # Validate specific commands in hook
        command_words = hook_command.split()
        for word in command_words[:3]:  # Check first 3 words
            word_clean = word.strip("'\"")
            if word_clean in self.BASH_TO_POWERSHELL or any(
                tool in word_clean.lower() for tool in ["black", "pytest", "git", "npm"]
            ):
                available, msg = self.validate_tool_availability(word_clean)
                if not available:
                    warnings.append(msg)

        return len(warnings) == 0 or all("⚠️" not in w for w in warnings), warnings

    def get_platform_specific_timeout(self, event_type: str) -> int:
        """
        Get appropriate timeout for event type, adjusted for platform.

        Args:
            event_type: Hook event type (PostToolUse, SessionStart, etc)

        Returns:
            Timeout in seconds
        """
        base_timeouts = {
            "PostToolUse": 60,
            "SubagentStop": 30,
            "SessionStart": 15,
            "PreToolUse": 10,
            "UserPromptSubmit": 5,
            "Stop": 10,
            "PrePush": 30
        }

        base_timeout = base_timeouts.get(event_type, 30)

        # Windows may need longer timeouts for some operations
        if self.is_windows:
            return int(base_timeout * 1.5)

        return base_timeout

    def get_platform_specific_shell(self) -> str:
        """Get appropriate shell for this platform."""
        if self.is_windows:
            return "powershell"
        else:
            return "bash"

    @staticmethod
    def _escape_bash_quotes(command: str) -> str:
        """Escape quotes for bash -c command."""
        return command.replace("'", "'\\''")

    def get_installation_instructions(self) -> str:
        """Get platform-specific installation instructions."""
        if self.is_windows:
            return """
## Windows Installation

Hook Factory on Windows requires:

1. **PowerShell** (built-in, usually available)
2. **Required tools**:
   - Git: `winget install git.git` or https://git-scm.com
   - Python: `winget install python` or https://python.org
   - Node.js: `winget install nodejs` or https://nodejs.org

3. **Installation**:
   ```powershell
   python installer.py install generated-hooks\\[hook-name] user
   ```

4. **Limitations**:
   - Some Unix-specific commands may not translate
   - File paths use backslashes (handled automatically)
   - PowerShell execution policy may need adjustment:
     ```powershell
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     ```

## Troubleshooting

If hooks don't work:
1. Check PowerShell execution policy
2. Verify tools are installed and in PATH
3. Review Claude Code logs in `%USERPROFILE%\\.claude\\logs\\`
4. Test command manually in PowerShell
"""
        else:
            return """
## Unix Installation (macOS/Linux)

Hook Factory on Unix requires:

1. **Bash shell** (default on macOS/Linux)
2. **Required tools**:
   - Git: `brew install git` (macOS) or `apt-get install git` (Linux)
   - Python: `brew install python3` or system package manager
   - Node.js: `brew install node` or system package manager

3. **Installation**:
   ```bash
   python3 installer.py install generated-hooks/[hook-name] user
   ```

## Troubleshooting

If hooks don't work:
1. Check bash is available: `which bash`
2. Verify tools are installed and in PATH
3. Check file permissions: `ls -la ~/.claude/hooks/`
4. Review Claude Code logs: `tail -f ~/.claude/logs/claude.log`
5. Test command manually in bash
"""


def get_platform_adapter() -> PlatformAdapter:
    """Factory function to get platform adapter."""
    return PlatformAdapter()


if __name__ == "__main__":
    adapter = PlatformAdapter()
    print(f"Current Platform: {adapter.get_platform_name()}")
    print(f"Is Windows: {adapter.is_windows}")
    print(f"Is Unix: {adapter.is_unix}")

    # Test command translation
    print("\n" + "=" * 60)
    print("Command Translation Examples")
    print("=" * 60)

    test_commands = [
        "black file.py",
        "pytest tests/",
        "git status",
        "npm test"
    ]

    for cmd in test_commands:
        translated, warning = adapter.translate_command(cmd)
        print(f"\nOriginal: {cmd}")
        print(f"Translated: {translated}")
        if warning:
            print(f"Note: {warning}")

    # Test installation instructions
    print("\n" + "=" * 60)
    print("Platform-Specific Instructions")
    print("=" * 60)
    print(adapter.get_installation_instructions())
