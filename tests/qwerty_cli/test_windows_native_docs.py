from pathlib import Path


def test_windows_native_install_path_docs_match_installer() -> None:
    doc = Path("website/docs/user-guide/windows-native.md").read_text()
    install = Path("scripts/install.ps1").read_text()

    assert "%LOCALAPPDATA%\\qwerty\\qwerty-agent\\venv\\Scripts" in doc
    assert "Get-Command qwerty        # should print C:\\Users\\<you>\\AppData\\Local\\qwerty\\qwerty-agent\\venv\\Scripts\\qwerty.exe" in doc
    assert '$qwertyBin = "$InstallDir\\venv\\Scripts"' in install
