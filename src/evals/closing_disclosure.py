from braintrust import Eval
from autoevals import AnswerCorrectness
from src.environment import init_environment
from src.parsing.pdf_loader import load_pdf_as_query_engine

def setup_chat():
    pinecone_index = init_environment()
    query_engine = load_pdf_as_query_engine("pdfs/disclosures.pdf", pinecone_index)
    return query_engine

llm = setup_chat()

def run_evals():
    Eval(
        "Closing Disclosure",
        scores=[AnswerCorrectness],
        task=lambda input: llm.query(input),
        data=lambda: [
            {
                "input": "what is the name of the settlement agent?",
                "expected": "Sarah Arnold",
            },
            {
                "input": "what is the address of the home that is being sold in this transaction?",
                "expected": "456 Somewhere Ave, Anytown, ST 12345",
            },
        ],
    )
