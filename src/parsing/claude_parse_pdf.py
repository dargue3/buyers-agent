from anthropic import Anthropic
import base64
from ..chat.printer import pretty_print
from src.utils.files import ask_user_for_file_path

def analyze_pdf_with_claude(pdf_path=None):
    """Analyze a PDF document using Claude's API"""
    if pdf_path is None:
        pdf_path = ask_user_for_file_path()

    # Read the PDF file and encode it
    with open(pdf_path, 'rb') as f:
        pdf_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Read the prompt template
    with open('prompts/read_home_inspection.md', 'r') as f:
        prompt_template = f.read()

    # Initialize Claude client
    client = Anthropic()
    
    # Send the API request
    message = client.beta.messages.create(
        max_tokens=8192,
        model="claude-3-5-sonnet-20241022",
        betas=["pdfs-2024-09-25", "prompt-caching-2024-07-31"],
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt_template
                    }
                ]
            }
        ],
    )

    # Extract the text content from the message
    text_content = ""
    for content in message.content:
        if isinstance(content, dict) and content.get("type") == "text":
            text_content += content.get("text", "")
    
    return text_content

if __name__ == "__main__":
    response = analyze_pdf_with_claude()
    pretty_print(response)
