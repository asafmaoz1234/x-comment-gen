import json
import os
from typing import Dict, Any, List
import openai
from datetime import datetime
import tweepy
from prompt_builder import build_prompt
from utils.input_sanitizer import ContentSanitizer
from x_poster import post_to_x
from utils.logger_util import logger

content_sanitizer = ContentSanitizer()


def load_prompt_template():
    """
    Load the prompt template from file.
    """
    try:
        filename = 'prompts/comment_prompt.txt'
        with open(filename, 'r') as file:
            return file.read()
    except Exception as e:
        logger.error(f'Error loading reply_prompt template: {str(e)}')
        # Fallback prompts
        return "You are a social media manager.\nCreate a friendly reply to: {topic}\nTone: {tone}"


def lambda_handler(event: Dict[Any, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler that processes SQS messages,
    generates content using OpenAI, and post a comment on X.
    """
    request_id = context.aws_request_id if context else 'local'
    logger.info('Starting lambda execution', extra={'extra_data': {'request_id': request_id}})

    try:
        # Initialize OpenAI client
        openai.api_key = os.environ['OPENAI_API_KEY']
        model = os.environ.get('OPENAI_MODEL', 'gpt-4')

        # Process based on event type
        message = json.loads(event['Records'][0]['body'])
        logger.info('Processing SQS REPLY message', extra={'extra_data': {'message': message}})
        message['post'] = content_sanitizer.sanitize_text(message['post'])

        # Load reply prompt template
        prompt_template = load_prompt_template()
        prompt = build_prompt(message, prompt_template)

        # Generate response using OpenAI
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt}
            ],
            max_tokens=280,
            temperature=0.7
        )
        content = response.choices[0].message.content.strip()
        # Initialize X API client
        x_client = tweepy.Client(
            consumer_key=os.environ['X_CONSUMER_KEY'],
            consumer_secret=os.environ['X_CONSUMER_SECRET'],
            access_token=os.environ['X_ACCESS_TOKEN'],
            access_token_secret=os.environ['X_ACCESS_TOKEN_SECRET']
        )

        # Post the reply
        comment_id = post_to_x(x_client, content, message['post_id'])
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully posted a reply to X post',
                'timestamp': datetime.utcnow().isoformat()
            })
        }
    except Exception as e:
        logger.error('Error in lambda execution',
                     extra={'extra_data': {'error': str(e)}},
                     exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            })
        }