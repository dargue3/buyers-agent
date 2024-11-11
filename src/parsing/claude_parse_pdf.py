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

    return message.content

if __name__ == "__main__":
    # response = analyze_pdf_with_claude()
    response = """
I\'ll analyze this home inspection report carefully, using my inner monologue to identify and categorize issues.\n\nLet me review the report methodically...\n\nI notice this is a property at 678 Connie Avenue in San Mateo, CA. The inspection was conducted on 9/18/2024. Looking through the findings...\n\nI see several concerning patterns emerging. Let me organize these by area and severity:\n\n<findings>\n<area name="Electrical">\n<critical_issues>\n1. Federal Pacific Electric Company electrical panel identified - known for product defects and potential fire hazards\n2. Exposed and unprotected electrical wiring in kitchen island cabinets\n3. Worn insulation on electrical service entrance connections exposing live conductor connectors\n</critical_issues>\n<major_issues>\n1. Missing cover plate at 240-volt receptacle in garage near water heater\n2. No AFCI protection installed in building\n3. Unable to confirm presence of electrical grounding electrode\n</major_issues>\n<minor_issues>\n1. Damaged doorbell button\n2. Damaged cover latch at main electrical panel\n</minor_issues>\n</area>\n\n<area name="Exterior">\n<critical_issues>\n1. Damage/deterioration in plywood siding at left side, right side and rear\n2. Damage/deterioration in fascia boards at multiple locations\n</critical_issues>\n<major_issues>\n1. Deterioration in eave boards at multiple locations\n2. Poor drainage - downspouts discharge next to building, risking foundation issues\n3. Corrosion and evidence of past leakage at exterior main water shut-off valve\n</major_issues>\n<minor_issues>\n1. Weathered/peeling paint in various locations\n2. Small to moderate cracks in driveway, patio and walkways\n3. Trip hazards from lifted/settled right side patio\n</minor_issues>\n</area>\n\n<area name="Plumbing">\n<critical_issues>\n1. Corroded galvanized steel water supply lines nearing end of useful life\n</critical_issues>\n<major_issues>\n1. Water heater temperature/pressure relief valve discharge pipe improperly terminated\n2. No drain pan installed under water heater\n3. No gas valve shut-off wrench near meter\n</major_issues>\n<minor_issues>\n1. Missing back-flow prevention devices at hose bibs\n2. No T-pipe extension on water heater gas supply piping\n</minor_issues>\n</area>\n\n<area name="Roof">\n<major_issues>\n1. Evidence of past pooling water on roof surface\n2. Wear and tear to roofing surface with loose/damaged material at front\n3. Cracked/eroded mortar cap at chimney top\n</major_issues>\n<minor_issues>\n1. Unpainted ABS plastic plumbing vents above roofline\n2. Mastic flashings at rooftop penetrations showing wear\n3. Boiler condensate drain improperly discharging onto roof surface\n</minor_issues>\n</area>\n\n<area name="Interior">\n<major_issues>\n1. Left and middle bedroom windows too high for emergency egress (>44" from floor)\n2. Sloped floors in living room and master bedroom indicating possible settlement\n3. Older smoke alarms that may not be reliable\n</major_issues>\n<minor_issues>\n1. Missing center floor guide at left rear bedroom closet doors\n2. Worn/torn window screens\n3. Deteriorated mortar/bricks in fireplace\n</minor_issues>\n</area>\n\n</findings>\n\n<summary>\nThis 68-year-old home presents several significant concerns that warrant careful consideration. The most pressing issues are:\n\n1. The Federal Pacific Electric panel, which is a known safety hazard and should be considered for immediate replacement.\n2. Deteriorating exterior components (siding, fascia, eaves) that could lead to water intrusion and further damage.\n3. Aging plumbing system with corroded galvanized pipes that may need comprehensive replacement.\n4. Signs of structural settlement indicated by sloped floors and foundation concerns.\n5. Multiple electrical safety issues requiring professional attention.\n\nWhile many of the issues are typical for a home of this age, the combination of electrical, plumbing, and structural concerns suggests significant updating and repairs may be needed. A buyer should carefully consider these factors when evaluating this property, as several of the identified issues could require substantial investment to address properly.\n</summary>
 """
    print(response)
