from unittest.mock import MagicMock, patch
import pytest
from src.data_access import db_handler
from src.core_data import VERBS # For initializing preferences in tests

# Mock the Supabase client for testing
@pytest.fixture
def mock_supabase_client():
        with patch('src.config.supabase', autospec=True) as mock_client:
            # Ensure the mock client is not None for the db_handler functions
            # Removed mock_client.__bool__ = MagicMock(return_value=True) as it caused AttributeError
            yield mock_client

@pytest.fixture
def mock_supabase_table():
    mock_table = MagicMock()
    # Mock the chain of calls for select, insert, upsert
    mock_table.select.return_value.eq.return_value.execute.return_value.data = []
    mock_table.insert.return_value.execute.return_value.data = []
    mock_table.upsert.return_value.execute.return_value.data = []
    return mock_table

@pytest.fixture(autouse=True)
def setup_db_handler_mocks(mock_supabase_client, mock_supabase_table):
    mock_supabase_client.table.return_value = mock_supabase_table
    # Ensure that db_handler uses the mocked supabase client
    db_handler.supabase = mock_supabase_client
    yield

class TestDbHandler:
    def test_load_results_empty(self, mock_supabase_table):
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = []
        results = db_handler.load_results()
        assert results == {}
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', db_handler.DEFAULT_USER_ID)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_load_results_with_data(self, mock_supabase_table):
        mock_data = [
            {"id": "1", "user_id": db_handler.DEFAULT_USER_ID, "verb": "falar", "tense": "present", "pronoun": "eu", "user_answer": "falo", "is_correct": True, "timestamp": "2023-01-01T12:00:00Z"},
            {"id": "2", "user_id": db_handler.DEFAULT_USER_ID, "verb": "comer", "tense": "past", "pronoun": "tu", "user_answer": "comeste", "is_correct": False, "timestamp": "2023-01-01T12:01:00Z"}
        ]
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = mock_data
        results = db_handler.load_results()
        expected_results = {
            "falar_present": {"eu": {"user_answer": "falo", "correct": True, "timestamp": "2023-01-01T12:00:00Z"}},
            "comer_past": {"tu": {"user_answer": "comeste", "correct": False, "timestamp": "2023-01-01T12:01:00Z"}}
        }
        assert results == expected_results
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', db_handler.DEFAULT_USER_ID)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_save_result(self, mock_supabase_table):
        result_data = {"user_id": db_handler.DEFAULT_USER_ID, "verb": "falar", "tense": "present", "pronoun": "eu", "user_answer": "falo", "is_correct": True}
        db_handler.save_result(result_data)
        mock_supabase_table.insert.assert_called_once_with([result_data])
        mock_supabase_table.insert.return_value.execute.assert_called_once()

    def test_load_sentences_empty(self, mock_supabase_table):
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = []
        sentences = db_handler.load_sentences()
        assert sentences == []
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', db_handler.DEFAULT_USER_ID)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_load_sentences_with_data(self, mock_supabase_table):
        mock_data = [
            {"id": "s1", "user_id": db_handler.DEFAULT_USER_ID, "verb": "ir", "tense": "present", "pronoun": "eu", "correct_form": "vou", "sentence": "Eu vou.", "is_correct": True, "timestamp": "2023-01-01T13:00:00Z"}
        ]
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = mock_data
        sentences = db_handler.load_sentences()
        assert sentences == mock_data
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', db_handler.DEFAULT_USER_ID)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_save_sentence(self, mock_supabase_table):
        sentence_data = {"user_id": db_handler.DEFAULT_USER_ID, "verb": "ir", "tense": "present", "pronoun": "eu", "correct_form": "vou", "sentence": "Eu vou.", "is_correct": True}
        db_handler.save_sentence(sentence_data)
        mock_supabase_table.insert.assert_called_once_with([sentence_data])
        mock_supabase_table.insert.return_value.execute.assert_called_once()

    def test_load_preferences_empty(self, mock_supabase_table):
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = []
        preferences = db_handler.load_preferences()
        
        # Expected preferences should be the default ones from core_data.VERBS
        expected_preferences = {verb: {tense: {"never_show": False, "always_show": False, "show_primarily": False}
                                     for tense in VERBS[verb]}
                              for verb in VERBS}
        assert preferences == expected_preferences
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', db_handler.DEFAULT_USER_ID)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_load_preferences_with_data(self, mock_supabase_table):
        mock_data = [
            {"id": "p1", "user_id": db_handler.DEFAULT_USER_ID, "verb": "falar", "tense": "present", "never_show": False, "always_show": True, "show_primarily": False},
            {"id": "p2", "user_id": db_handler.DEFAULT_USER_ID, "verb": "comer", "tense": "past", "never_show": True, "always_show": False, "show_primarily": True}
        ]
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = mock_data
        preferences = db_handler.load_preferences()
        
        # Start with default preferences and then apply mock data
        expected_preferences = {verb: {tense: {"never_show": False, "always_show": False, "show_primarily": False}
                                     for tense in VERBS[verb]}
                              for verb in VERBS}
        
        # Manually apply the mock data to the expected preferences
        expected_preferences["falar"]["present"] = {"never_show": False, "always_show": True, "show_primarily": False}
        expected_preferences["comer"]["past"] = {"never_show": True, "always_show": False, "show_primarily": True}

        assert preferences == expected_preferences
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', db_handler.DEFAULT_USER_ID)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_save_preference_new(self, mock_supabase_table):
        preference_data = {"user_id": db_handler.DEFAULT_USER_ID, "verb": "falar", "tense": "present", "never_show": False, "always_show": True, "show_primarily": False}
        db_handler.save_preference(preference_data)
        mock_supabase_table.upsert.assert_called_once_with(preference_data, on_conflict='user_id,verb,tense')
        mock_supabase_table.upsert.return_value.execute.assert_called_once()

    def test_load_results_with_specific_user_id(self, mock_supabase_table):
        test_user_id = "test_user_123"
        mock_data = [
            {"id": "1", "user_id": test_user_id, "verb": "falar", "tense": "present", "pronoun": "eu", "user_answer": "falo", "is_correct": True, "timestamp": "2023-01-01T12:00:00Z"}
        ]
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = mock_data
        results = db_handler.load_results(user_id=test_user_id)
        expected_results = {
            "falar_present": {"eu": {"user_answer": "falo", "correct": True, "timestamp": "2023-01-01T12:00:00Z"}}
        }
        assert results == expected_results
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', test_user_id)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_save_result_with_specific_user_id(self, mock_supabase_table):
        test_user_id = "test_user_123"
        result_data = {"user_id": test_user_id, "verb": "falar", "tense": "present", "pronoun": "eu", "user_answer": "falo", "is_correct": True}
        db_handler.save_result(result_data, user_id=test_user_id)
        mock_supabase_table.insert.assert_called_once_with([result_data])
        mock_supabase_table.insert.return_value.execute.assert_called_once()

    def test_load_sentences_with_specific_user_id(self, mock_supabase_table):
        test_user_id = "test_user_123"
        mock_data = [
            {"id": "s1", "user_id": test_user_id, "verb": "ir", "tense": "present", "pronoun": "eu", "correct_form": "vou", "sentence": "Eu vou.", "is_correct": True, "timestamp": "2023-01-01T13:00:00Z"}
        ]
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = mock_data
        sentences = db_handler.load_sentences(user_id=test_user_id)
        assert sentences == mock_data
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', test_user_id)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_save_sentence_with_specific_user_id(self, mock_supabase_table):
        test_user_id = "test_user_123"
        sentence_data = {"user_id": test_user_id, "verb": "ir", "tense": "present", "pronoun": "eu", "correct_form": "vou", "sentence": "Eu vou.", "is_correct": True}
        db_handler.save_sentence(sentence_data, user_id=test_user_id)
        mock_supabase_table.insert.assert_called_once_with([sentence_data])
        mock_supabase_table.insert.return_value.execute.assert_called_once()

    def test_load_preferences_with_specific_user_id(self, mock_supabase_table):
        test_user_id = "test_user_123"
        mock_data = [
            {"id": "p1", "user_id": test_user_id, "verb": "falar", "tense": "present", "never_show": False, "always_show": True, "show_primarily": False}
        ]
        mock_supabase_table.select.return_value.eq.return_value.execute.return_value.data = mock_data
        preferences = db_handler.load_preferences(user_id=test_user_id)
        
        expected_preferences = {verb: {tense: {"never_show": False, "always_show": False, "show_primarily": False}
                                     for tense in VERBS[verb]}
                              for verb in VERBS}
        expected_preferences["falar"]["present"] = {"never_show": False, "always_show": True, "show_primarily": False}

        assert preferences == expected_preferences
        mock_supabase_table.select.assert_called_with('*')
        mock_supabase_table.select.return_value.eq.assert_called_with('user_id', test_user_id)
        mock_supabase_table.select.return_value.eq.return_value.execute.assert_called_once()

    def test_save_preference_with_specific_user_id(self, mock_supabase_table):
        test_user_id = "test_user_123"
        preference_data = {"user_id": test_user_id, "verb": "falar", "tense": "present", "never_show": False, "always_show": True, "show_primarily": False}
        db_handler.save_preference(preference_data, user_id=test_user_id)
        mock_supabase_table.upsert.assert_called_once_with(preference_data, on_conflict='user_id,verb,tense')
        mock_supabase_table.upsert.return_value.execute.assert_called_once()

    def test_save_preference_update(self, mock_supabase_table):
        preference_data = {"user_id": db_handler.DEFAULT_USER_ID, "verb": "falar", "tense": "present", "never_show": True, "always_show": False, "show_primarily": False}
        db_handler.save_preference(preference_data)
        mock_supabase_table.upsert.assert_called_once_with(preference_data, on_conflict='user_id,verb,tense')
        mock_supabase_table.upsert.return_value.execute.assert_called_once()
