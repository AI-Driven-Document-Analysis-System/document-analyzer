"""
Enhanced search modes for RAG chatbot including query rephrasing and multiple queries
"""
import logging
from typing import List, Dict, Any, Optional
from langchain.llms.base import BaseLLM
from langchain.schema import Document
import asyncio

logger = logging.getLogger(__name__)


class QueryRephraser:
    """Service for rephrasing user queries to improve search results"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def rephrase_query(self, original_query: str) -> str:
        """
        Rephrase a user query to make it clearer and more searchable
        
        Args:
            original_query: The original user query
            
        Returns:
            Rephrased query string
        """
        try:
            rephrase_prompt = f"""
You are an expert at rephrasing search queries to improve retrieval accuracy.

Original question: "{original_query}"

Please rephrase this question to be more specific, clear, and better suited for semantic search. 

Return ONLY the rephrased question, nothing else. Do not include explanations, formatting, or additional text.

Rephrased question:"""

            # Debug: Check what type of LLM we have
            logger.info(f"LLM type: {type(self.llm)}")
            logger.info(f"LLM methods: {[method for method in dir(self.llm) if not method.startswith('_')]}")

            rephrased = original_query  # Default fallback
            
            # Try different LLM invocation methods
            try:
                if hasattr(self.llm, 'ainvoke'):
                    # Modern LangChain ChatModel approach
                    response = await self.llm.ainvoke(rephrase_prompt)
                    logger.info(f"ainvoke response type: {type(response)}")
                    logger.info(f"ainvoke response: {response}")
                    
                    if hasattr(response, 'content'):
                        rephrased = response.content.strip()
                    elif isinstance(response, str):
                        rephrased = response.strip()
                    else:
                        rephrased = str(response).strip()
                        
                elif hasattr(self.llm, 'agenerate'):
                    # Legacy LLM approach
                    response = await self.llm.agenerate([rephrase_prompt])
                    logger.info(f"agenerate response type: {type(response)}")
                    
                    if hasattr(response, 'generations') and response.generations:
                        generation = response.generations[0][0]
                        if hasattr(generation, 'text'):
                            rephrased = generation.text.strip()
                        else:
                            rephrased = str(generation).strip()
                    else:
                        rephrased = str(response).strip()
                        
                else:
                    # Sync fallback
                    if hasattr(self.llm, 'invoke'):
                        response = self.llm.invoke(rephrase_prompt)
                        logger.info(f"invoke response type: {type(response)}")
                        
                        if hasattr(response, 'content'):
                            rephrased = response.content.strip()
                        elif isinstance(response, str):
                            rephrased = response.strip()
                        else:
                            rephrased = str(response).strip()
                    else:
                        logger.warning("No suitable LLM method found, using original query")
                        
            except Exception as llm_error:
                logger.error(f"LLM invocation error: {llm_error}")
                logger.error(f"LLM error type: {type(llm_error)}")
                rephrased = original_query
            
            # Clean up the response - extract just the rephrased question
            if rephrased.startswith('"') and rephrased.endswith('"'):
                rephrased = rephrased[1:-1]
            
            # Extract the actual question if it's buried in explanatory text
            lines = rephrased.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('This rephrased') and not line.startswith('Here\'s') and not line.startswith('1.') and not line.startswith('2.') and not line.startswith('3.') and not line.startswith('4.'):
                    # Remove quotes if present
                    if line.startswith('"') and line.endswith('"'):
                        line = line[1:-1]
                    # If this looks like a question, use it
                    if '?' in line or len(line) > 20:
                        rephrased = line
                        break
            
            logger.info(f"Query rephrased from: '{original_query}' to: '{rephrased}'")
            return rephrased
            
        except Exception as e:
            logger.error(f"Error rephrasing query: {e}")
            logger.error(f"Exception type: {type(e)}")
            return original_query


class MultipleQueriesGenerator:
    """Service for generating multiple related queries from a single user query"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
    
    async def generate_multiple_queries(self, original_query: str, num_queries: int = 3) -> List[str]:
        """
        Generate multiple related queries from a single user query
        
        Args:
            original_query: The original user query
            num_queries: Number of queries to generate (default: 3)
            
        Returns:
            List of related query strings
        """
        try:
            multiple_queries_prompt = f"""
You are an expert at breaking down complex questions into multiple focused sub-questions for comprehensive document search.

Original question: "{original_query}"

Generate {num_queries} related but distinct questions that would help provide a comprehensive answer to the original question. Each question should:
1. Focus on a different aspect of the original question
2. Be specific and searchable
3. Help gather complete information on the topic
4. Avoid redundancy with other generated questions

Format your response as a numbered list:
1. [First question]
2. [Second question]
3. [Third question]"""

            # Try different LLM invocation methods
            generated_text = ""
            try:
                if hasattr(self.llm, 'ainvoke'):
                    # Modern LangChain ChatModel approach
                    response = await self.llm.ainvoke(multiple_queries_prompt)
                    
                    if hasattr(response, 'content'):
                        generated_text = response.content.strip()
                    elif isinstance(response, str):
                        generated_text = response.strip()
                    else:
                        generated_text = str(response).strip()
                        
                elif hasattr(self.llm, 'agenerate'):
                    # Legacy LLM approach
                    response = await self.llm.agenerate([multiple_queries_prompt])
                    
                    if hasattr(response, 'generations') and response.generations:
                        generation = response.generations[0][0]
                        if hasattr(generation, 'text'):
                            generated_text = generation.text.strip()
                        else:
                            generated_text = str(generation).strip()
                    else:
                        generated_text = str(response).strip()
                        
                else:
                    # Sync fallback
                    if hasattr(self.llm, 'invoke'):
                        response = self.llm.invoke(multiple_queries_prompt)
                        
                        if hasattr(response, 'content'):
                            generated_text = response.content.strip()
                        elif isinstance(response, str):
                            generated_text = response.strip()
                        else:
                            generated_text = str(response).strip()
                    else:
                        logger.warning("No suitable LLM method found for multiple queries")
                        
            except Exception as llm_error:
                logger.error(f"LLM invocation error in multiple queries: {llm_error}")
                generated_text = ""
            
            # Parse the numbered list
            queries = []
            lines = generated_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Remove numbering and clean up
                    query = line.split('.', 1)[-1].strip()
                    if query.startswith('[') and query.endswith(']'):
                        query = query[1:-1]
                    # Remove markdown formatting
                    if query.startswith('**') and query.endswith('**'):
                        query = query[2:-2]
                    # Remove any remaining asterisks
                    query = query.replace('**', '').replace('*', '')
                    if query:
                        queries.append(query)
            
            # Ensure we have the requested number of queries
            if len(queries) < num_queries:
                # Add the original query if we don't have enough
                queries.append(original_query)
            
            # Limit to requested number
            queries = queries[:num_queries]
            
            logger.info(f"Generated {len(queries)} queries from: '{original_query}'")
            for i, query in enumerate(queries, 1):
                logger.info(f"  {i}. {query}")
                
            return queries
            
        except Exception as e:
            logger.error(f"Error generating multiple queries: {e}")
            return [original_query]


class EnhancedSearchEngine:
    """Enhanced search engine that supports different search modes"""
    
    def __init__(self, retriever, llm: BaseLLM):
        self.retriever = retriever
        self.query_rephraser = QueryRephraser(llm)
        self.multiple_queries_generator = MultipleQueriesGenerator(llm)
    
    async def search_standard(self, query: str, k: int = 5) -> List[Document]:
        """
        Standard search mode - direct query search
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        try:
            logger.info(f"[STANDARD] Using standard search for query: '{query}'")
            print(f"[STANDARD] Direct query search")
            documents = self.retriever.get_relevant_documents(query)
            logger.info(f"[STANDARD] Search returned {len(documents[:k])} documents")
            return documents[:k]
        except Exception as e:
            logger.error(f"Error in standard search: {e}")
            return []
    
    async def search_rephrase(self, query: str, k: int = 5) -> List[Document]:
        """
        Rephrase search mode - rephrase query then search
        
        Args:
            query: Original search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents from rephrased query
        """
        try:
            logger.info(f"[REPHRASE] Using rephrase search for query: '{query}'")
            print(f"[REPHRASE] Query rephrasing + search")
            
            # Rephrase the query
            rephrased_query = await self.query_rephraser.rephrase_query(query)
            print(f"Original: '{query}'")
            print(f"Rephrased: '{rephrased_query}'")
            
            # Search with rephrased query
            documents = self.retriever.get_relevant_documents(rephrased_query)
            
            # Add metadata to indicate this was from a rephrased query
            for doc in documents:
                if hasattr(doc, 'metadata'):
                    doc.metadata['original_query'] = query
                    doc.metadata['rephrased_query'] = rephrased_query
                    doc.metadata['search_mode'] = 'rephrase'
            
            logger.info(f"[REPHRASE] Search returned {len(documents[:k])} documents")
            return documents[:k]
            
        except Exception as e:
            logger.error(f"Error in rephrase search: {e}")
            print(f"[ERROR] Rephrase search failed, falling back to standard search")
            # Fallback to standard search
            return await self.search_standard(query, k)
    
    async def search_multiple_queries(self, query: str, k: int = 5) -> List[Document]:
        """
        Multiple queries search mode - generate multiple queries and combine results
        
        Args:
            query: Original search query
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents from multiple queries
        """
        try:
            logger.info(f"[MULTIPLE] Using multiple queries search for query: '{query}'")
            print(f"[MULTIPLE] Generate multiple queries + combine results")
            
            # Generate multiple related queries
            queries = await self.multiple_queries_generator.generate_multiple_queries(query, num_queries=3)
            print(f"Generated {len(queries)} sub-queries:")
            for i, sub_query in enumerate(queries, 1):
                print(f"   {i}. {sub_query}")
            
            # Search with each query
            all_documents = []
            seen_content = set()
            
            for i, sub_query in enumerate(queries):
                try:
                    print(f"Searching with sub-query {i+1}: '{sub_query}'")
                    documents = self.retriever.get_relevant_documents(sub_query)
                    
                    # Add metadata and deduplicate
                    for doc in documents:
                        # Use content hash for deduplication
                        content_hash = hash(doc.page_content)
                        if content_hash not in seen_content:
                            seen_content.add(content_hash)
                            
                            if hasattr(doc, 'metadata'):
                                doc.metadata['original_query'] = query
                                doc.metadata['sub_query'] = sub_query
                                doc.metadata['sub_query_index'] = i
                                doc.metadata['search_mode'] = 'multiple_queries'
                            
                            all_documents.append(doc)
                            
                except Exception as e:
                    logger.warning(f"Error searching with sub-query '{sub_query}': {e}")
                    print(f"[ERROR] Sub-query {i+1} failed: {e}")
                    continue
            
            # Sort by relevance score if available, otherwise keep order
            try:
                # Try to sort by score if available in metadata
                all_documents.sort(key=lambda x: x.metadata.get('score', 0), reverse=True)
            except:
                pass
            
            logger.info(f"[MULTIPLE] Search returned {len(all_documents)} unique documents")
            print(f"Combined results: {len(all_documents)} unique documents found")
            return all_documents[:k]
            
        except Exception as e:
            logger.error(f"Error in multiple queries search: {e}")
            print(f"[ERROR] Multiple queries search failed, falling back to standard search")
            # Fallback to standard search
            return await self.search_standard(query, k)
    
    async def search(self, query: str, search_mode: str = "standard", k: int = 5) -> List[Document]:
        """
        Main search method that routes to appropriate search mode
        
        Args:
            query: Search query
            search_mode: Search mode ('standard', 'rephrase', 'multiple_queries')
            k: Number of documents to retrieve
            
        Returns:
            List of relevant documents
        """
        print(f"\n{'='*60}")
        print(f"[ENHANCED SEARCH] MODE: {search_mode.upper()}")
        print(f"Query: '{query}'")
        print(f"{'='*60}")
        
        if search_mode == "rephrase":
            return await self.search_rephrase(query, k)
        elif search_mode == "multiple_queries":
            return await self.search_multiple_queries(query, k)
        else:
            return await self.search_standard(query, k)
