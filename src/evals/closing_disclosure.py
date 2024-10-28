from ..environment import get_openai_env_vars
from ..parsing.llama_parse_pdf import load_pdf_as_query_engine

from braintrust import Eval
from autoevals import Factuality

llm = load_pdf_as_query_engine("pdfs/disclosures.pdf")

api_key, base_url = get_openai_env_vars()

def run_evals():
    Eval(
        name="Closing Disclosure",
        scores=[Factuality(api_key=api_key, base_url=base_url)],
        task=lambda input: llm.query(input).response,
        data=lambda: [
            {
                "input": "what is the first and last name of the settlement agent?",
                "expected": "Sarah Arnold",
            },
            {
                "input": "what is the address of the home that is being sold in this transaction?",
                "expected": "456 Somewhere Ave, Anytown, ST 12345",
            },
            {
                "input": "how much can the buyer expect to pay per month in their first year of ownership?",
                "expected": "$1,050.26",
            },
            {
                "input": "how much cash in total was given to the seller in this transaction?",
                "expected": "$64,414.96",
            },
            {
                "input": "Answer Yes or no, does the state law protect the buyer from liability for the unpaid balance if their lender forecloses?",
                "expected": "Yes",
            },
            {
                "input": "Answer Yes or no, has this contract been signed by both parties?",
                "expected": "No",
            },
        ],
    )
