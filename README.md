# X Post Reply Generator

An AWS Lambda function that automatically generates and posts engaging replies to X (formerly Twitter) posts using OpenAI's GPT models.

## Features

- Automatically generates contextual replies to X posts using OpenAI's GPT models
- Maintains specified tone and character count requirements
- Includes comprehensive input sanitization
- Structured JSON logging
- Proper error handling and validation
- AWS Lambda-ready with deployment scripts

## Prerequisites

- Python 3.11+
- AWS account with Lambda access
- X Developer Account with API access
- OpenAI API access
- Required environment variables:
    - `OPENAI_API_KEY`: Your OpenAI API key
    - `OPENAI_MODEL`: OpenAI model to use (defaults to gpt-4)
    - `X_CONSUMER_KEY`: X API consumer key
    - `X_CONSUMER_SECRET`: X API consumer secret
    - `X_ACCESS_TOKEN`: X API access token
    - `X_ACCESS_TOKEN_SECRET`: X API access token secret

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd x-post-reply-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create deployment package:
```bash
chmod +x build-function-zip.sh
./build-function-zip.sh
```

## Project Structure

```
├── main.py                 # Lambda handler and main logic
├── prompt_builder.py       # OpenAI prompt construction
├── x_poster.py            # X posting functionality
├── requirements.txt       # Python dependencies
├── build-function-zip.sh  # Deployment package creation script
├── utils/
│   ├── logger_util.py     # JSON logging configuration
│   └── input_sanitizer.py # Input validation and sanitization
└── prompts/
    └── comment_prompt.txt # OpenAI system prompt template
```

## Usage

The Lambda function expects an SQS event with the following JSON structure:

```json
{
  "post": "Original X post content",
  "post_id": "X post ID to reply to",
  "tone": "desired tone (e.g., professional, casual)",
  "min_char_count": "minimum character count for the reply"
}
```

### Local Testing

1. Set up environment variables:
```bash
export OPENAI_API_KEY="your-key"
export X_CONSUMER_KEY="your-key"
export X_CONSUMER_SECRET="your-secret"
export X_ACCESS_TOKEN="your-token"
export X_ACCESS_TOKEN_SECRET="your-token-secret"
```

2. Run tests:
```bash
pytest
```

## Deployment

1. Run the build script to create deployment package:
```bash
./build-function-zip.sh
```

2. Upload the generated `function.zip` to AWS Lambda
3. Configure environment variables in AWS Lambda
4. Set up an SQS trigger for the Lambda function

## Security Features

- Input sanitization to prevent XSS, command injection, and SQL injection
- Environment variable configuration for sensitive credentials
- Proper error handling and logging
- API credential validation before posting

## Error Handling

The system includes comprehensive error handling for:
- Invalid API credentials
- Missing permissions
- Rate limiting
- Network issues
- Input validation failures

All errors are logged with proper context and returned in the Lambda response.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.