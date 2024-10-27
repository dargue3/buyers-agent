from .environment import init_environment
from .parsing.pdf_loader import get_query_engine_from_pinecone
from .evals.closing_disclosure import run_evals

pinecone_index = init_environment()

query_engine = get_query_engine_from_pinecone(pinecone_index)

run_evals()