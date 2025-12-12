#!/usr/bin/env python3
"""
Test script for GUI rename functionality.
Tests the FileRenamerThread without the full GUI.
"""

import sys
import tempfile
from pathlib import Path

# Add parent directory to path to import gui module
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtCore import QCoreApplication
from gui import FileRenamerThread


def test_file_renamer_thread():
    """Test the FileRenamerThread class."""
    print("=" * 60)
    print("Testing FileRenamerThread")
    print("=" * 60)

    # Create QCoreApplication (required for QThread)
    app = QCoreApplication(sys.argv)

    # Create a temporary directory with test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test files
        test_files = [
            "photo_003.jpg",
            "photo_001.jpg",
            "photo_002.jpg",
            "image100text.png",
            "document25.txt",
        ]

        print(f"\nCreating test files in: {temp_path}")
        for filename in test_files:
            (temp_path / filename).write_text(f"Content: {filename}")
            print(f"  Created: {filename}")

        # Test 1: Dry run with sequential renaming
        print("\n" + "-" * 60)
        print("Test 1: Sequential renaming (dry run)")
        print("-" * 60)

        test_passed = [False]  # Use list to allow modification in nested function

        def on_log(message):
            print(f"LOG: {message}")

        def on_progress(value):
            print(f"PROGRESS: {value}%")

        def on_finished(stats):
            print(f"\nFINISHED: {stats}")
            test_passed[0] = True
            app.quit()

        thread = FileRenamerThread(
            temp_path,
            sort_type='name',
            rename_type='sequential',
            prefix='img_',
            suffix='',
            dry_run=True
        )

        thread.log.connect(on_log)
        thread.progress.connect(on_progress)
        thread.finished.connect(on_finished)

        thread.start()
        app.exec()

        if test_passed[0]:
            print("\n✓ Test 1 passed: Dry run completed successfully")
        else:
            print("\n✗ Test 1 failed: Dry run did not complete")
            return False

        # Verify files were NOT renamed (dry run)
        files_after_dry_run = list(temp_path.iterdir())
        original_names = {f.name for f in files_after_dry_run}
        expected_original = {'photo_001.jpg', 'photo_002.jpg', 'photo_003.jpg', 'image100text.png', 'document25.txt'}

        if original_names == expected_original:
            print("✓ Files were not modified (dry run worked correctly)")
        else:
            print(f"✗ Files were modified during dry run! Found: {original_names}")
            return False

        # Test 2: Actual renaming
        print("\n" + "-" * 60)
        print("Test 2: Sequential renaming (actual)")
        print("-" * 60)

        # Create new app for second test
        app2 = QCoreApplication(sys.argv)
        test_passed[0] = False

        def on_finished2(stats):
            print(f"\nFINISHED: {stats}")
            test_passed[0] = stats['successful'] == 5 and stats['failed'] == 0
            app2.quit()

        thread2 = FileRenamerThread(
            temp_path,
            sort_type='name',
            rename_type='sequential',
            prefix='img_',
            suffix='_final',
            dry_run=False
        )

        thread2.log.connect(on_log)
        thread2.progress.connect(on_progress)
        thread2.finished.connect(on_finished2)

        thread2.start()
        app2.exec()

        if test_passed[0]:
            print("\n✓ Test 2 passed: Actual renaming completed successfully")
        else:
            print("\n✗ Test 2 failed: Renaming did not complete successfully")
            return False

        # Verify files were renamed
        files_after_rename = list(temp_path.iterdir())
        renamed_names = {f.name for f in files_after_rename}

        print(f"\nFiles after renaming: {sorted(renamed_names)}")

        # Files should be renamed in alphabetical order: document25.txt, image100text.png, photo_001.jpg, photo_002.jpg, photo_003.jpg
        expected_renamed = {'img_1_final.txt', 'img_2_final.png', 'img_3_final.jpg', 'img_4_final.jpg', 'img_5_final.jpg'}
        if renamed_names == expected_renamed:
            print("✓ Files were renamed correctly!")
            return True
        else:
            print(f"✗ Unexpected filenames!")
            print(f"  Expected: {sorted(expected_renamed)}")
            print(f"  Got: {sorted(renamed_names)}")
            return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("GUI RENAME FUNCTIONALITY TEST")
    print("=" * 60)

    try:
        success = test_file_renamer_thread()

        print("\n" + "=" * 60)
        if success:
            print("✓ ALL TESTS PASSED!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("✗ SOME TESTS FAILED")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
