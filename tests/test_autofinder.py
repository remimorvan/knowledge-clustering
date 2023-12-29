"""
Tests for the autofinder module.
"""

from pathlib import Path

from knowledge_clustering.autofinder import (
    NoFile,
    TooManyFiles,
    get_unique_diagnose_file,
    get_knowledge_files,
)


def test_autofinder() -> None:
    """Test function for the functions get_unique_diagnose_file, get_knowledge_files
    from the module autofinder."""
    p = Path("tests/testaf/")
    p.mkdir()
    test_results = [False] * 6
    # 0th test with 1 diagnose file and 3 .kl with a unique default file (OK)
    (p / "subdir1").mkdir()
    (p / "subdir2").mkdir()
    (p / "subdir3").mkdir()
    (p / "subdir1/coolproject.diagnose").touch()
    (p / "subdir2/abbreviations.kl").touch()
    (p / "subdir2/main-default.kl").touch()
    (p / "subdir3/omega-automata.kl").touch()
    # Content of testaf directory:
    # - subdir1
    # |-- coolproject.diagnose
    # - subdir2
    # |-- abbreviations.kl
    # |-- main-default.kl
    # - subdir3
    # |-- omega-automata.kl
    try:
        dg_file = get_unique_diagnose_file(p)
        kl_files = get_knowledge_files(p)
        if (
            str(dg_file) == "tests/testaf/subdir1/coolproject.diagnose"
            and len(kl_files) == 3
            and str(kl_files[2]) == "tests/testaf/subdir2/main-default.kl"
        ):
            test_results[0] = True
    except (NoFile, TooManyFiles):
        pass
    # 1st test with 1 diagnose file and 4 .kl with a two default files (not OK)
    (p / "subdir3/secondary-default.kl").touch()
    # Content of testaf directory:
    # - subdir1
    # |-- coolproject.diagnose
    # - subdir2
    # |-- abbreviations.kl
    # |-- main-default.kl
    # - subdir3
    # |-- omega-automata.kl
    # |-- secondary-default.kl
    try:
        _ = get_knowledge_files(p)
    except TooManyFiles:
        test_results[1] = True
    # 2nd test with 1 diagnose file and 2 .kl with no default files (not OK)
    (p / "subdir2/main-default.kl").unlink()
    (p / "subdir3/secondary-default.kl").unlink()
    # Content of testaf directory:
    # - subdir1
    # |-- coolproject.diagnose
    # - subdir2
    # |-- abbreviations.kl
    # - subdir3
    # |-- omega-automata.kl
    try:
        _ = get_knowledge_files(p)
    except NoFile:
        test_results[2] = True
    # 3rd test with 1 diagnose file and 1 .kl with no default files (OK)
    (p / "subdir2/abbreviations.kl").unlink()
    # Content of testaf directory:
    # - subdir1
    # |-- coolproject.diagnose
    # - subdir2
    # - subdir3
    # |-- omega-automata.kl
    try:
        _ = get_knowledge_files(p)
        test_results[3] = True
    except (NoFile, TooManyFiles):
        pass
    # 4th test with 2 diagnose file and 1 .kl with no default files (not OK)
    (p / "subdir2/another-file.diagnose").touch()
    # Content of testaf directory:
    # - subdir1
    # |-- coolproject.diagnose
    # - subdir2
    # |-- another-file.diagnose
    # - subdir3
    # |-- omega-automata.kl
    try:
        _ = get_unique_diagnose_file(p)
    except TooManyFiles:
        test_results[4] = True
    # 5th test with no diagnose file and 1 .kl with no default files (not OK)
    (p / "subdir1/coolproject.diagnose").unlink()
    (p / "subdir2/another-file.diagnose").unlink()
    # Content of testaf directory:
    # - subdir1
    # - subdir2
    # - subdir3
    # |-- omega-automata.kl
    try:
        _ = get_unique_diagnose_file(p)
    except NoFile:
        test_results[5] = True
    # Remove all files and directory created for the test
    (p / "subdir3/omega-automata.kl").unlink()
    for dirname in ["subdir3", "subdir2", "subdir1", ""]:
        (p / dirname).rmdir()
    assert all(test_results)
