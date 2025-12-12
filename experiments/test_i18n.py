#!/usr/bin/env python3
"""
Test script to verify internationalization (i18n) implementation.
Tests both English and Russian translations.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from translations import Translations, get_translator, tr


def test_translations():
    """Test translation functionality."""
    print("Testing Internationalization (i18n) Implementation")
    print("=" * 60)

    # Test 1: Create English translator
    print("\nTest 1: English Translation")
    print("-" * 60)
    translator_en = Translations("en")

    test_keys = [
        "window_title",
        "ready",
        "tab_video_resize",
        "tab_file_download",
        "tab_file_rename",
        "language",
        "language_en",
        "language_ru",
    ]

    all_passed = True
    for key in test_keys:
        value = translator_en.get(key)
        if value and value != key:
            print(f"✓ {key}: {value}")
        else:
            print(f"✗ {key}: MISSING")
            all_passed = False

    # Test 2: Create Russian translator
    print("\nTest 2: Russian Translation")
    print("-" * 60)
    translator_ru = Translations("ru")

    for key in test_keys:
        value = translator_ru.get(key)
        if value and value != key:
            print(f"✓ {key}: {value}")
        else:
            print(f"✗ {key}: MISSING")
            all_passed = False

    # Test 3: Test formatting with arguments
    print("\nTest 3: Translation with Arguments")
    print("-" * 60)

    # English
    msg_en = translator_en.get("videos_found", 5, "/test/folder")
    print(f"EN: {msg_en}")

    # Russian
    msg_ru = translator_ru.get("videos_found", 5, "/test/folder")
    print(f"RU: {msg_ru}")

    # Test 4: Test language switching
    print("\nTest 4: Language Switching")
    print("-" * 60)
    global_translator = get_translator()

    print(f"Initial language: {global_translator.language}")
    print(f"Initial text: {global_translator.get('ready')}")

    global_translator.set_language("ru")
    print(f"After switch to RU: {global_translator.get('ready')}")

    global_translator.set_language("en")
    print(f"After switch back to EN: {global_translator.get('ready')}")

    # Test 5: Verify all required keys exist in both languages
    print("\nTest 5: Verify All Keys Exist in Both Languages")
    print("-" * 60)

    en_keys = set(Translations.EN.keys())
    ru_keys = set(Translations.RU.keys())

    missing_in_ru = en_keys - ru_keys
    missing_in_en = ru_keys - en_keys

    if missing_in_ru:
        print(f"✗ Keys missing in Russian: {missing_in_ru}")
        all_passed = False
    else:
        print("✓ All English keys present in Russian")

    if missing_in_en:
        print(f"✗ Keys missing in English: {missing_in_en}")
        all_passed = False
    else:
        print("✓ All Russian keys present in English")

    print(f"\nTotal keys: {len(en_keys)}")

    # Test 6: Check for GUI-specific keys
    print("\nTest 6: GUI-Specific Keys")
    print("-" * 60)

    gui_keys = [
        "video_title",
        "download_title",
        "rename_title",
        "settings",
        "browse",
        "start_processing",
        "start_download",
        "start_rename",
        "stop",
        "zero_padding",
        "zero_padding_hint",
        "dry_run"
    ]

    for key in gui_keys:
        en_val = translator_en.get(key)
        ru_val = translator_ru.get(key)
        if en_val != key and ru_val != key:
            print(f"✓ {key}: EN='{en_val}' RU='{ru_val}'")
        else:
            print(f"✗ {key}: MISSING in one or both languages")
            all_passed = False

    # Final result
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All i18n tests PASSED!")
        return True
    else:
        print("✗ Some i18n tests FAILED!")
        return False


if __name__ == "__main__":
    passed = test_translations()
    sys.exit(0 if passed else 1)
