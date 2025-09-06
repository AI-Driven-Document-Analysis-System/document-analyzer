import os
import sys
import warnings
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
api_key = os.getenv("GEMINI_API_KEY")

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

vectorstore = LangChainChromaStore("./chroma_db", "forecasting_docs")
llm = LLMFactory.create_gemini_llm(api_key, "gemini-1.5-flash")
retriever = vectorstore.as_retriever()
chain = CustomConversationalChain(llm, retriever)

chunker = DocumentChunker(chunk_size=500, chunk_overlap=100)
indexer = LangChainDocumentIndexer(vectorstore, chunker)

test_doc = {
    'id': 'forecasting-1',
    'text': 'Time-series forecasting is crucial in the efficient operation and decision-making processes of various industrial systems. Accurately predicting future trends is essential for optimizing resources, production scheduling, and overall system performance. This comprehensive review examines time-series forecasting models and their applications across diverse industries. We discuss the fundamental principles, strengths, and weaknesses of traditional statistical methods such as Autoregressive Integrated Moving Average (ARIMA) and Exponential Smoothing (ES), which are widely used due to their simplicity and interpretability. However, these models often struggle with the complex, non-linear, and high-dimensional data commonly found in industrial systems. To address these challenges, we explore Machine Learning techniques, including Support Vector Machine (SVM) and Artificial Neural Network (ANN). These models offer more flexibility and adaptability, often outperforming traditional statistical methods. Furthermore, we investigate the potential of hybrid models, which combine the strengths of different methods to achieve improved prediction performance. These hybrid models result in more accurate and robust forecasts. Finally, we discuss the potential of newly developed generative models such as Generative Adversarial Network (GAN) for time-series forecasting. This review emphasizes the importance of carefully selecting the appropriate model based on specific industry requirements, data characteristics, and forecasting objectives.',
    'filename': 'forecasting_review.txt',
    'user_id': 'test-user'
}

# Index document silently
with SuppressOutput():
    try:
        ids = indexer.index_document(test_doc)
    except Exception as e:
        pass

questions = [
    "What are the main limitations of traditional statistical methods in industrial forecasting?",
    "How do hybrid models address the weaknesses of individual forecasting approaches?",
    "What makes generative models like GANs potentially valuable for time-series forecasting?",
    "Why might ARIMA models struggle with high-dimensional industrial data?",
    "What factors should be considered when selecting a forecasting model for a specific industry?"
]

for i, question in enumerate(questions, 1):
    print(f"{BLUE}Question {i}: {question}{RESET}")
    try:
        with SuppressOutput():
            result = chain.run(question)
        print(f"{GREEN}Answer: {result['answer']}{RESET}")
    except Exception as e:
        print(f"{GREEN}Answer: Query failed{RESET}")
    print()
