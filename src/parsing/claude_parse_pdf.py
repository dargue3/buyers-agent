import anthropic
import base64
from src.utils.files import ask_user_for_file_path

def analyze_pdf_with_claude(pdf_path=None):
    """Analyze a PDF document using Claude's API"""
    if pdf_path is None:
        pdf_path = ask_user_for_file_path()

    # Read the PDF file and encode it
    with open(pdf_path, 'rb') as f:
        pdf_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Read the prompt template
    with open('prompt.md', 'r') as f:
        prompt_template = f.read()

    # Initialize Claude client
    client = anthropic.Anthropic()
    
    # Send the API request
    message = client.beta.messages.create(
        model="claude-3-opus-20240229",
        betas=["pdfs-2024-09-25"],
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

    return message.content

if __name__ == "__main__":
    response = analyze_pdf_with_claude()
    print(response)
