import os
import sys
import warnings
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api_key = os.getenv("GROQ_API_KEY")

# Add the project root to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Suppress all warnings
warnings.filterwarnings("ignore")

# Suppress all logging and verbose output
os.environ['LANGCHAIN_TRACING_V2'] = 'false'
os.environ['LANGCHAIN_ENDPOINT'] = ''
os.environ['LANGCHAIN_API_KEY'] = ''
os.environ['LANGCHAIN_PROJECT'] = ''
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from app.services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from app.services.chatbot.chains.conversational_chain import CustomConversationalChain
from app.services.chatbot.llm.llm_factory import LLMFactory
from app.services.chatbot.vector_db.chunking import DocumentChunker
from app.services.chatbot.vector_db.indexing import LangChainDocumentIndexer


# Redirect stdout to suppress verbose output
class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout


# Colors for output
BLUE = '\033[94m'
GREEN = '\033[92m'
RESET = '\033[0m'

if not api_key:
    print(f"{GREEN}GROQ_API_KEY not set in .env; skipping Groq test.{RESET}")
else:
    vectorstore = LangChainChromaStore("./test_chroma_db", "groq_docs")
    llm = LLMFactory.create_groq_llm(api_key, model="llama-3.1-8b-instant")
    retriever = vectorstore.as_retriever()
    chain = CustomConversationalChain(llm, retriever)

    chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
    indexer = LangChainDocumentIndexer(vectorstore, chunker)

    test_doc = {
        'id': 'groq-1',
        'text': 'Pursuant to the authority vested in the City Council under Chapter 3, Title II of the Municipal Charter,'
                ' it shall be unlawful for any person to generate, cause, or permit any sound exceeding seventy (70)'
                ' decibels as measured at the property line between the hours of 10:00 p.m. and 7:00 a.m., except as '
                'expressly permitted herein. Exemptions to this section shall include emergency response activities, public '
                'safety operations, and activities for which a special event permit has been duly issued by the Department '
                'of Public Affairs. Violations of this ordinance shall constitute a civil infraction subject to a fine not'
                ' to exceed five hundred dollars ($500) per occurrence, with each day of continued violation constituting a '
                'separate and distinct offense. Enforcement of this section shall be undertaken by the Office of Code Compliance '
                'in coordination with the Police Department.',
        'filename': 'groq_info.txt',
        'user_id': 'test-user'
    }

    # Index document silently
    with SuppressOutput():
        try:
            ids = indexer.index_document(test_doc)
        except Exception:
            pass

    questions = [
        "What is the maximum decibel level allowed during restricted hours?",
        "What are the restricted hours mentioned in this ordinance?",
        "What exemptions are provided in this ordinance?",
        "What is the maximum fine for violating this ordinance?",
        "Which departments are responsible for enforcing this ordinance?"
    ]

    for i, question in enumerate(questions, 1):
        print(f"{BLUE}Question {i}: {question}{RESET}")
        try:
            with SuppressOutput():
                result = chain.run(question)
            print(f"{GREEN}Answer: {result['answer']}{RESET}")
        except Exception:
            print(f"{GREEN}Answer: Query failed{RESET}")
        print()


