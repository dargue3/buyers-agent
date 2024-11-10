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
    with open('prompts/home_inspection.md', 'r') as f:
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

    return message.content

if __name__ == "__main__":
    # response = analyze_pdf_with_claude()
    response ="""
Based on my analysis of the home inspection report, here are the identified issues organized by severity:\n\n<issues>\n<major_concerns>\n\n1. Zinsco Electrical Breakers in Main Service and Subpanel\n- Location: Electrical panels\n- Reason for concern: Becoming substandard in the industry\n- Potential implications: Safety hazard, potential electrical failures\n\n2. Non-Tempered Glass Windows and Shower Doors\n- Location: Throughout house and master bathroom\n- Reason for concern: Safety hazard\n- Potential implications: Risk of injury if glass breaks\n\n3. Garage Door Safety Issues\n- Location: Garage\n- Reason for concern: Safety reverse not operating, door opens outward over step\n- Potential implications: Serious safety hazard, especially for children or pets\n\n4. Water Heater Installation Problems\n- Location: Garage\n- Reason for concern: Multiple issues including improper seismic strapping, unbonded supply lines, improper TP valve drain\n- Potential implications: Safety hazard during earthquake, potential water damage\n\n5. Foam Roofing Damage\n- Location: Roof\n- Reason for concern: Visible damage to roofing material\n- Potential implications: Potential water intrusion and structural damage\n\n</major_concerns>\n\n<minor_concerns>\n\n1. Exterior Maintenance Issues\n- Location: Various exterior locations\n- Notes: Eave gaps, trim paint damage, garage door bottom gap needs sealing\n\n2. Plumbing Issues\n- Location: Master bathroom\n- Notes: Leak at shower head connection, shower head escutcheon not sealed in hall bathroom\n\n3. Foundation and Drainage Issues\n- Location: Right exterior foundation\n- Notes: Efflorescence indicating moisture presence, garage foundation vent needs proper screening\n\n4. Heating System Issues\n- Location: Bedroom #2\n- Notes: Radiant heat not operational in one bedroom\n\n5. Fireplace Maintenance\n- Location: Living room\n- Notes: Minor creosote buildup in chimney flue, needs cleaning\n\n6. Garage Floor\n- Location: Garage\n- Notes: Cracks present, needs repair to prevent further damage\n\n</minor_concerns>\n</issues>\n\n<summary>\nThe home inspection revealed several significant concerns that require immediate attention, particularly regarding safety and major systems. The electrical system's Zinsco breakers are a notable concern due to their substandard nature. Safety hazards include non-tempered glass throughout the house and garage door safety issues. The water heater's installation does not meet current requirements and needs multiple corrections.\n\nWhile the home appears to be in generally functional condition, there are numerous maintenance issues that should be addressed. The combination of roofing issues, plumbing problems, and foundation concerns suggests the property needs comprehensive updating of various systems and components. Many of these issues, while not immediately critical, could develop into more serious problems if left unaddressed.\n\nPotential buyers should carefully consider the costs associated with addressing these issues, particularly the electrical system upgrades and safety-related corrections, which could represent significant expenses. A qualified licensed contractor should be consulted for detailed evaluation and cost estimates for the required repairs.\n</summary>
"""
    pretty_print(response)
