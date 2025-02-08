from typing import Dict, Any

from utils.logger_util import logger


def build_prompt(message: Dict[Any, Any], template: str) -> str:
    """
    Builds a prompt for OpenAI based on the event data and template.
    """
    logger.info('Starting reply comments prompt building')
    post = message.get('post', '')
    tone = message.get('tone', 'professional')
    min_char_count = message.get('min_char_count', '100')

    formatted_prompt = template.format(
        post=post,
        tone=tone,
        min_char_count=min_char_count
    )

    logger.info('Prompt building completed', extra={'extra_data': {'prompt': formatted_prompt}})
    return formatted_prompt