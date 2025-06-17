import pytest
from src.services.exercise_service import select_exercises
from src.core_data import VERBS

@pytest.fixture
def mock_preferences_full():
    return {
        "verbs": ["hablar", "comer", "vivir", "ser", "estar", "ir", "hacer", "tener", "poder", "decir"],
        "tenses": ["presente", "preterito", "futuro"]
    }

@pytest.fixture
def mock_preferences_limited():
    return {
        "verbs": ["hablar", "comer"],
        "tenses": ["presente"]
    }

@pytest.fixture
def mock_preferences_empty():
    return {
        "verbs": [],
        "tenses": []
    }

def test_select_exercises_successful_selection(mocker, mock_preferences_full):
    """
    Scenario 1: Successful Exercise Selection (Happy Path)
    Given: A mock file_handler.load_preferences() that returns a preferences dictionary with available verbs and tenses.
    When: select_exercises(num_exercises=5) is called.
    Then: It should return a list of 5 unique exercise tuples (verb, tense), where each verb and tense is valid according to the mocked preferences.
    """
    mocker.patch('src.data_access.db_handler.load_preferences', return_value=mock_preferences_full)
    mocker.patch('src.data_access.db_handler.load_results', return_value={}) # Ensure no results interfere

    # Create a VERBS mock that includes all verbs and tenses from mock_preferences_full
    # The actual conjugations don't matter for select_exercises, just their existence
    mock_verbs_data = {}
    for verb in mock_preferences_full["verbs"]:
        mock_verbs_data[verb] = {}
        for tense in mock_preferences_full["tenses"]:
            mock_verbs_data[verb][tense] = ["conjugation1", "conjugation2"] # Dummy conjugations

    mocker.patch('src.services.exercise_service.VERBS', new=mock_verbs_data)

    num_exercises = 5
    exercises = select_exercises(num_exercises)

    assert len(exercises) == num_exercises
    assert len(set(exercises)) == num_exercises  # Ensure uniqueness
    for verb, tense in exercises:
        assert verb in mock_preferences_full["verbs"]
        assert tense in mock_preferences_full["tenses"]
        # Assert against the mocked VERBS, not the original VERBS
        assert verb in mock_verbs_data and tense in mock_verbs_data[verb]

def test_select_exercises_not_enough_available(mocker, mock_preferences_limited):
    """
    Scenario 2: Not Enough Exercises Available
    Given: A mock file_handler.load_preferences() that returns preferences with fewer than 5 *possible* unique exercises.
    When: select_exercises(num_exercises=5) is called.
    Then: It should return a list containing all available unique exercises, even if fewer than num_exercises.
    """
    mocker.patch('src.data_access.db_handler.load_preferences', return_value=mock_preferences_limited)
    mocker.patch('src.data_access.db_handler.load_results', return_value={}) # Ensure no results interfere

    # Create a VERBS mock that includes only the limited verbs and tenses
    mock_verbs_data = {
        "hablar": {"presente": ["hablo", "hablas"]},
        "comer": {"presente": ["como", "comes"]}
    }
    mocker.patch('src.services.exercise_service.VERBS', new=mock_verbs_data)

    num_exercises = 5
    exercises = select_exercises(num_exercises)

    expected_exercises = [("hablar", "presente"), ("comer", "presente")]
    assert len(exercises) == len(expected_exercises)
    assert set(exercises) == set(expected_exercises)
    for verb, tense in exercises:
        assert verb in mock_preferences_limited["verbs"]
        assert tense in mock_preferences_limited["tenses"]
        # Assert against the mocked VERBS, not the original VERBS
        assert verb in mock_verbs_data and tense in mock_verbs_data[verb]

def test_select_exercises_no_exercises_available(mocker, mock_preferences_empty):
    """
    Scenario 3: No Exercises Available
    Given: A mock file_handler.load_preferences() that returns an empty preferences dictionary or one with no available verbs/tenses.
    When: select_exercises(num_exercises=5) is called.
    Then: It should return an empty list [].
    """
    mocker.patch('src.data_access.db_handler.load_preferences', return_value=mock_preferences_empty)
    mocker.patch('src.data_access.db_handler.load_results', return_value={}) # Ensure no results interfere
    mocker.patch('src.services.exercise_service.VERBS', new={}) # No verbs available

    num_exercises = 5
    exercises = select_exercises(num_exercises)

    assert exercises == []
