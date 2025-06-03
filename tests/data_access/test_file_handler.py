import pytest
import json
from unittest import mock

# Module to test
from src.data_access import file_handler

@pytest.fixture
def mock_open_file(mocker):
    """Fixture to mock builtins.open."""
    # We use 'src.data_access.file_handler.open' if open is imported like 'from x import open'
    # but since it's using the global open(), we mock 'builtins.open'
    # However, to be more precise and ensure we only mock open for the module under test,
    # it's often better to patch it where it's used if possible, or ensure the test
    # environment doesn't let the mock leak.
    # For file_handler.py, 'open' is used directly as the built-in.
    # The path for patching should be where 'open' is looked up by the code under test.
    # If file_handler.py does `import builtins; builtins.open`, then 'src.data_access.file_handler.builtins.open'.
    # If it just calls `open()`, then 'builtins.open' is generally correct for Pytest mocker.
    # Let's assume direct use of built-in open.
    return mocker.patch('builtins.open', new_callable=mock.mock_open)

@pytest.fixture
def mock_json_load(mocker):
    """Fixture to mock json.load."""
    # This mocks json.load globally. For more targeted mocking,
    # you could patch 'src.data_access.file_handler.json.load'
    # if json was imported as 'import json' in file_handler.py
    return mocker.patch('json.load')

def test_load_results_success(mock_open_file, mock_json_load):
    """Test load_results returns data when file exists and is valid JSON."""
    expected_data = {"key": "value"}
    # Configure the mock for json.load
    mock_json_load.return_value = expected_data
    
    # Configure the mock for open().read_data
    # mock_open_file.return_value.read.return_value = json.dumps(expected_data) # Not needed if json.load is mocked

    actual_data = file_handler.load_results()

    # Check that open was called correctly
    # file_handler.RESULTS_FILE is imported from src.config
    # We need to ensure that this path is consistent or also controlled if it varies.
    # For now, assume file_handler.RESULTS_FILE is a fixed, known string.
    mock_open_file.assert_called_once_with(file_handler.RESULTS_FILE, 'r')
    # Check that json.load was called (it will be called with the file object from open)
    mock_json_load.assert_called_once() 
    assert actual_data == expected_data

def test_load_results_file_not_found(mock_open_file, mock_json_load):
    """Test load_results returns empty dict if FileNotFoundError."""
    mock_open_file.side_effect = FileNotFoundError

    actual_data = file_handler.load_results()

    mock_open_file.assert_called_once_with(file_handler.RESULTS_FILE, 'r')
    mock_json_load.assert_not_called() # json.load should not be called if file not found
    assert actual_data == {}

def test_load_results_empty_file_json_decode_error(mock_open_file, mock_json_load):
    """Test load_results returns empty dict if JSONDecodeError (e.g., empty file)."""
    # open() itself doesn't fail, but json.load does
    mock_json_load.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)

    actual_data = file_handler.load_results()

    mock_open_file.assert_called_once_with(file_handler.RESULTS_FILE, 'r')
    mock_json_load.assert_called_once() # json.load is attempted
    assert actual_data == {}

def test_load_results_invalid_json_decode_error(mock_open_file, mock_json_load):
    """Test load_results returns empty dict if JSONDecodeError (invalid JSON content)."""
    # open() itself doesn't fail, but json.load does
    mock_json_load.side_effect = json.JSONDecodeError("Extra data", "doc", 0) 

    actual_data = file_handler.load_results()

    mock_open_file.assert_called_once_with(file_handler.RESULTS_FILE, 'r')
    mock_json_load.assert_called_once() # json.load is attempted
    assert actual_data == {}

@pytest.fixture
def mock_json_dump(mocker):
    """Fixture to mock json.dump."""
    return mocker.patch('json.dump')

def test_save_results_success(mock_open_file, mock_json_dump):
    """Test save_results correctly writes valid data to file."""
    data_to_save = {"test_key": "test_value", "number": 123}
    
    file_handler.save_results(data_to_save)

    mock_open_file.assert_called_once_with(file_handler.RESULTS_FILE, 'w')
    mock_json_dump.assert_called_once_with(data_to_save, mock_open_file(), indent=4)
    # Verify the content written to the mock file handle
    # This requires accessing the mock_open_file's write calls
    # mock_open_file().write.assert_called_once_with(json.dumps(data_to_save, indent=4)) # This is implicitly covered by json.dump mock

def test_save_results_empty_dict(mock_open_file, mock_json_dump):
    """Test save_results correctly writes an empty dictionary to file."""
    data_to_save = {}

    file_handler.save_results(data_to_save)

    mock_open_file.assert_called_once_with(file_handler.RESULTS_FILE, 'w')
    mock_json_dump.assert_called_once_with(data_to_save, mock_open_file(), indent=4)

def test_load_sentences_success(mock_open_file, mock_json_load):
    """Test load_sentences returns data when file exists and is valid JSON list."""
    expected_data = ["sentence one", "sentence two"]
    mock_json_load.return_value = expected_data

    actual_data = file_handler.load_sentences()

    mock_open_file.assert_called_once_with(file_handler.SENTENCES_FILE, 'r')
    mock_json_load.assert_called_once()
    assert actual_data == expected_data

def test_load_sentences_file_not_found(mock_open_file, mock_json_load):
    """Test load_sentences returns empty list if FileNotFoundError."""
    mock_open_file.side_effect = FileNotFoundError

    actual_data = file_handler.load_sentences()

    mock_open_file.assert_called_once_with(file_handler.SENTENCES_FILE, 'r')
    mock_json_load.assert_not_called()
    assert actual_data == []

def test_load_sentences_empty_file_json_decode_error(mock_open_file, mock_json_load):
    """Test load_sentences returns empty list if JSONDecodeError (e.g., empty file)."""
    mock_json_load.side_effect = json.JSONDecodeError("Expecting value", "doc", 0)

    actual_data = file_handler.load_sentences()

    mock_open_file.assert_called_once_with(file_handler.SENTENCES_FILE, 'r')
    mock_json_load.assert_called_once()
    assert actual_data == []

def test_save_sentences_success(mock_open_file, mock_json_dump):
    """Test save_sentences correctly writes valid list data to file."""
    data_to_save = ["new sentence 1", "new sentence 2"]
    
    file_handler.save_sentences(data_to_save)

    mock_open_file.assert_called_once_with(file_handler.SENTENCES_FILE, 'w')
    mock_json_dump.assert_called_once_with(data_to_save, mock_open_file(), indent=4)

def test_save_sentences_empty_list(mock_open_file, mock_json_dump):
    """Test save_sentences correctly writes an empty list to file."""
    data_to_save = []

    file_handler.save_sentences(data_to_save)

    mock_open_file.assert_called_once_with(file_handler.SENTENCES_FILE, 'w')
    mock_json_dump.assert_called_once_with(data_to_save, mock_open_file(), indent=4)

# Mock VERBS for preferences regeneration
MOCK_VERBS_FOR_PREFS = {
    "hablar": ["presente", "pasado"],
    "comer": ["presente"]
}

@pytest.fixture
def mock_verbs(mocker):
    """Fixture to mock src.core_data.VERBS."""
    return mocker.patch('src.data_access.file_handler.VERBS', new=MOCK_VERBS_FOR_PREFS)

def test_load_preferences_success(mock_open_file, mock_json_load, mock_verbs):
    """Test load_preferences returns data when file exists and is valid JSON."""
    expected_data = {"hablar": {"presente": {"never_show": False, "always_show": False}}}
    mock_json_load.return_value = expected_data

    actual_data = file_handler.load_preferences()

    mock_open_file.assert_called_once_with(file_handler.PREFERENCES_FILE, 'r')
    mock_json_load.assert_called_once()
    assert actual_data == expected_data

def test_load_preferences_file_not_found_regenerates(mock_open_file, mock_json_load, mock_verbs, mocker):
    """Test load_preferences regenerates and saves if FileNotFoundError."""
    mock_open_file.side_effect = [FileNotFoundError, mock_open_file.return_value] # First open fails, second (for save) succeeds
    mock_json_load.side_effect = [json.JSONDecodeError("Expecting value", "doc", 0), None] # First load fails, second (for save) is not called
    
    # Mock save_preferences to prevent actual file write during test and avoid recursion
    mock_save_preferences = mocker.patch('src.data_access.file_handler.save_preferences')

    expected_regenerated_prefs = {
        "hablar": {"presente": {"never_show": False, "always_show": False}, "pasado": {"never_show": False, "always_show": False}},
        "comer": {"presente": {"never_show": False, "always_show": False}}
    }

    actual_data = file_handler.load_preferences()

    # Check that open was called for reading (which failed)
    mock_open_file.assert_any_call(file_handler.PREFERENCES_FILE, 'r')
    # Check that save_preferences was called with the regenerated data
    mock_save_preferences.assert_called_once_with(expected_regenerated_prefs)
    assert actual_data == expected_regenerated_prefs

def test_load_preferences_invalid_json_regenerates(mock_open_file, mock_json_load, mock_verbs, mocker):
    """Test load_preferences regenerates and saves if JSONDecodeError."""
    mock_json_load.side_effect = json.JSONDecodeError("Extra data", "doc", 0)
    
    # Mock save_preferences to prevent actual file write during test and avoid recursion
    mock_save_preferences = mocker.patch('src.data_access.file_handler.save_preferences')

    expected_regenerated_prefs = {
        "hablar": {"presente": {"never_show": False, "always_show": False}, "pasado": {"never_show": False, "always_show": False}},
        "comer": {"presente": {"never_show": False, "always_show": False}}
    }

    actual_data = file_handler.load_preferences()

    mock_open_file.assert_called_once_with(file_handler.PREFERENCES_FILE, 'r')
    mock_json_load.assert_called_once()
    mock_save_preferences.assert_called_once_with(expected_regenerated_prefs)
    assert actual_data == expected_regenerated_prefs

def test_save_preferences_success(mock_open_file, mock_json_dump):
    """Test save_preferences correctly writes valid data to file."""
    data_to_save = {"verb1": {"tense1": {"never_show": True}}}
    
    file_handler.save_preferences(data_to_save)

    mock_open_file.assert_called_once_with(file_handler.PREFERENCES_FILE, 'w')
    mock_json_dump.assert_called_once_with(data_to_save, mock_open_file(), indent=4)

def test_save_preferences_empty_dict(mock_open_file, mock_json_dump):
    """Test save_preferences correctly writes an empty dictionary to file."""
    data_to_save = {}

    file_handler.save_preferences(data_to_save)

    mock_open_file.assert_called_once_with(file_handler.PREFERENCES_FILE, 'w')
    mock_json_dump.assert_called_once_with(data_to_save, mock_open_file(), indent=4)

@pytest.fixture
def mock_os_path_exists(mocker):
    """Fixture to mock os.path.exists."""
    return mocker.patch('os.path.exists')

@pytest.fixture
def mock_os_makedirs(mocker):
    """Fixture to mock os.makedirs."""
    return mocker.patch('os.makedirs')

def test_ensure_data_files_all_exist(mock_os_path_exists, mock_os_makedirs, mock_open_file, mock_json_dump):
    """Test ensure_data_files does nothing if all files and dir exist."""
    mock_os_path_exists.side_effect = lambda path: True # All paths exist

    file_handler.ensure_data_files()

    mock_os_makedirs.assert_not_called()
    mock_open_file.assert_not_called()
    mock_json_dump.assert_not_called()

def test_ensure_data_files_none_exist(mock_os_path_exists, mock_os_makedirs, mock_open_file, mock_json_dump, mock_verbs):
    """Test ensure_data_files creates all files and dir if none exist."""
    # First call for data_dir, then for RESULTS_FILE, SENTENCES_FILE, PREFERENCES_FILE
    mock_os_path_exists.side_effect = [False, False, False, False] # data_dir, results, sentences, preferences

    # Expected preferences to be generated
    expected_regenerated_prefs = {
        "hablar": {"presente": {"never_show": False, "always_show": False}, "pasado": {"never_show": False, "always_show": False}},
        "comer": {"presente": {"never_show": False, "always_show": False}}
    }

    file_handler.ensure_data_files()

    # Check os.makedirs was called for data directory
    mock_os_makedirs.assert_called_once_with(file_handler.os.path.dirname(file_handler.RESULTS_FILE))

    # Check open and json.dump calls for each file
    # RESULTS_FILE
    mock_open_file.assert_any_call(file_handler.RESULTS_FILE, 'w')
    mock_json_dump.assert_any_call({}, mock.ANY) # Removed indent=4

    # SENTENCES_FILE
    mock_open_file.assert_any_call(file_handler.SENTENCES_FILE, 'w')
    mock_json_dump.assert_any_call([], mock.ANY) # Removed indent=4

    # PREFERENCES_FILE
    mock_open_file.assert_any_call(file_handler.PREFERENCES_FILE, 'w')
    mock_json_dump.assert_any_call(expected_regenerated_prefs, mock.ANY) # Removed indent=4

    # Ensure correct number of calls
    assert mock_open_file.call_count == 3
    assert mock_json_dump.call_count == 3

def test_ensure_data_files_some_missing(mock_os_path_exists, mock_os_makedirs, mock_open_file, mock_json_dump, mock_verbs):
    """Test ensure_data_files creates only missing files."""
    # Scenario: data_dir exists, RESULTS_FILE exists, SENTENCES_FILE and PREFERENCES_FILE are missing
    mock_os_path_exists.side_effect = [
        True,  # data_dir exists
        True,  # RESULTS_FILE exists
        False, # SENTENCES_FILE does not exist
        False  # PREFERENCES_FILE does not exist
    ]

    expected_regenerated_prefs = {
        "hablar": {"presente": {"never_show": False, "always_show": False}, "pasado": {"never_show": False, "always_show": False}},
        "comer": {"presente": {"never_show": False, "always_show": False}}
    }

    file_handler.ensure_data_files()

    mock_os_makedirs.assert_not_called() # data_dir already exists

    # Check open and json.dump calls only for missing files
    # RESULTS_FILE should NOT be opened/dumped
    mock_open_file.assert_any_call(file_handler.SENTENCES_FILE, 'w')
    mock_json_dump.assert_any_call([], mock.ANY) # Removed indent=4

    mock_open_file.assert_any_call(file_handler.PREFERENCES_FILE, 'w')
    mock_json_dump.assert_any_call(expected_regenerated_prefs, mock.ANY) # Removed indent=4

    # Ensure correct number of calls (only for sentences and preferences)
    assert mock_open_file.call_count == 2
    assert mock_json_dump.call_count == 2
