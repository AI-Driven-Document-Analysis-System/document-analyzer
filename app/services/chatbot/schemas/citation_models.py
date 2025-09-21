from pydantic import BaseModel, Field
from typing import List, Optional

class DocumentCitation(BaseModel):
    """Model for individual document citations with source tracking."""
    
    source_id: int = Field(
        description="The integer ID of the SPECIFIC document chunk that justifies the answer."
    )
    document_name: str = Field(
        description="The filename of the document that was cited."
    )
    quote: str = Field(
        description="The EXACT verbatim text from the source that was used to generate the answer."
    )
    # Removed confidence field - LLM explicitly chooses sources so confidence is always high

class CitedAnswer(BaseModel):
    """Model for answers with accurate source citations and exact quotes."""
    
    answer: str = Field(
        description="The answer to the user question, based only on the provided document sources."
    )
    citations: List[DocumentCitation] = Field(
        description="List of specific document chunks with exact quotes that were actually used to generate this answer."
    )
    has_sources: bool = Field(
        default=True,
        description="Whether this answer is based on document sources or general knowledge."
    )

# Legacy models kept for backward compatibility
class QuotedCitation(BaseModel):
    """Legacy model - use DocumentCitation instead."""
    
    source_id: int = Field(
        description="The integer ID of the SPECIFIC document chunk that justifies the answer."
    )
    document_name: str = Field(
        description="The filename of the document that was cited."
    )
    quote: str = Field(
        description="The VERBATIM quote from the specified source that justifies the answer."
    )
    # Removed confidence field for consistency

class QuotedAnswer(BaseModel):
    """Legacy model - use CitedAnswer instead."""
    
    answer: str = Field(
        description="The answer to the user question, based only on the provided document sources."
    )
    citations: List[QuotedCitation] = Field(
        description="List of specific document chunks with exact quotes that were used to generate this answer."
    )
    has_sources: bool = Field(
        default=True,
        description="Whether this answer is based on document sources or general knowledge."
    )
