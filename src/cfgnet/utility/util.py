def is_test_file(abs_file_path) -> bool:
    test_indicators = ["/tests", "test", "tests"]
    return any(indicator in abs_file_path for indicator in test_indicators)
