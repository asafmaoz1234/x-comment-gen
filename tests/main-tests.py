import pytest
from unittest.mock import Mock, patch
import json
from datetime import datetime
import tweepy
import openai
from main import lambda_handler
from prompt_builder import build_prompt
from x_poster import post_to_x
from utils.input_sanitizer import ContentSanitizer


@pytest.fixture
def mock_context():
    context = Mock()
    context.aws_request_id = "test-request-id"
    return context


@pytest.fixture
def sample_event():
    return {
        "Records": [{
            "body": json.dumps({
                "post": "Test post content",
                "post_id": "123456789",
                "tone": "professional",
                "min_char_count": "100"
            })
        }]
    }


@pytest.fixture
def mock_openai_response():
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message.content = "Generated response"
    return response


class TestXPoster:
    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup environment variables for each test"""
        self.test_env = {
            'OPENAI_API_KEY': 'test_key',
            'X_CONSUMER_KEY': 'test_consumer_key',
            'X_CONSUMER_SECRET': 'test_consumer_secret',
            'X_ACCESS_TOKEN': 'test_access_token',
            'X_ACCESS_TOKEN_SECRET': 'test_access_token_secret'
        }
        with patch.dict('os.environ', self.test_env):
            openai.api_key = self.test_env['OPENAI_API_KEY']
            yield

    @pytest.fixture
    def mock_tweepy_client(self):
        client = Mock()
        client.get_me.return_value = Mock()
        client.get_me.return_value.data = Mock()
        client.get_me.return_value.data.username = "test_user"
        return client

    def test_post_to_x_success(self, mock_tweepy_client):
        mock_tweepy_client.create_tweet.return_value = Mock(data={'id': '987654321'})

        result = post_to_x(mock_tweepy_client, "Test content", "123456789")

        assert result == '987654321'
        mock_tweepy_client.create_tweet.assert_called_once_with(
            in_reply_to_tweet_id="123456789",
            text="Test content"
        )

    def test_post_to_x_unauthorized(self, mock_tweepy_client):
        mock_tweepy_client.get_me.side_effect = tweepy.errors.Unauthorized(response=Mock())

        with pytest.raises(Exception) as exc_info:
            post_to_x(mock_tweepy_client, "Test content", "123456789")

        assert "Invalid X API credentials" in str(exc_info.value)

    def test_post_to_x_forbidden_write(self, mock_tweepy_client):
        mock_tweepy_client.get_me.side_effect = tweepy.errors.Forbidden(
            response=Mock(text="Write permissions required")
        )

        with pytest.raises(Exception) as exc_info:
            post_to_x(mock_tweepy_client, "Test content", "123456789")

        assert "write permissions" in str(exc_info.value).lower()


class TestPromptBuilder:
    def test_build_prompt_with_all_parameters(self):
        message = {
            "post": "Test post",
            "tone": "professional",
            "min_char_count": "100"
        }
        template = "Post: {post}, Tone: {tone}, Min chars: {min_char_count}"

        result = build_prompt(message, template)

        assert result == "Post: Test post, Tone: professional, Min chars: 100"

    def test_build_prompt_with_missing_parameters(self):
        message = {"post": "Test post"}
        template = "Post: {post}, Tone: {tone}, Min chars: {min_char_count}"

        result = build_prompt(message, template)

        assert "Test post" in result
        assert "professional" in result  # Default tone
        assert "100" in result  # Default min_char_count


class TestContentSanitizer:
    def test_sanitize_text_removes_dangerous_characters(self):
        sanitizer = ContentSanitizer()
        input_text = "Dangerous input' ; DROP TABLE users; --"

        result = sanitizer.sanitize_text(input_text)

        assert "'" not in result
        assert ";" not in result
        assert "--" not in result

    def test_sanitize_text_handles_none(self):
        sanitizer = ContentSanitizer()
        result = sanitizer.sanitize_text(None)
        assert result == ""


@patch('openai.chat.completions.create')
@patch('tweepy.Client')
def test_lambda_handler_success(mock_tweepy_client, mock_openai_create,
                                sample_event, mock_context, mock_openai_response):
    mock_openai_create.return_value = mock_openai_response
    mock_tweepy_client.return_value.create_tweet.return_value = Mock(data={'id': '987654321'})

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key',
        'X_CONSUMER_KEY': 'test-key',
        'X_CONSUMER_SECRET': 'test-secret',
        'X_ACCESS_TOKEN': 'test-token',
        'X_ACCESS_TOKEN_SECRET': 'test-token-secret'
    }):
        result = lambda_handler(sample_event, mock_context)

    assert result['statusCode'] == 200
    assert 'Successfully posted' in result['body']
    assert 'timestamp' in json.loads(result['body'])


@patch('openai.chat.completions.create')
def test_lambda_handler_error(mock_openai_create, sample_event, mock_context):
    mock_openai_create.side_effect = Exception("API Error")

    with patch.dict('os.environ', {
        'OPENAI_API_KEY': 'test-key'
    }):
        result = lambda_handler(sample_event, mock_context)

    assert result['statusCode'] == 500
    assert 'error' in json.loads(result['body'])
