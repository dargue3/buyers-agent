from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

def test_langchain():
    print("Testing LangChain installation...")
    try:
        # Just create a template - we won't actually call OpenAI yet
        prompt = PromptTemplate(
            input_variables=["topic"],
            template="Tell me about {topic}."
        )
        print("LangChain successfully imported!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_langchain()
