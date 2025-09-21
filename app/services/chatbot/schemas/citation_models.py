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
    confidence: float = Field(
        default=1.0,
        description="Confidence level that this source was actually used (0.0 to 1.0)."
    )

class CitedAnswer(BaseModel):
    """Model for answers with accurate source citations."""
    
    answer: str = Field(
        description="The answer to the user question, based only on the provided document sources."
    )
    citations: List[DocumentCitation] = Field(
        description="List of specific document chunks that were actually used to generate this answer."
    )
    has_sources: bool = Field(
        default=True,
        description="Whether this answer is based on document sources or general knowledge."
    )

class QuotedCitation(BaseModel):
    """Model for citations that include exact quotes from sources."""
    
    source_id: int = Field(
        description="The integer ID of the SPECIFIC document chunk that justifies the answer."
    )
    document_name: str = Field(
        description="The filename of the document that was cited."
    )
    quote: str = Field(
        description="The VERBATIM quote from the specified source that justifies the answer."
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence level that this source was actually used (0.0 to 1.0)."
    )

class QuotedAnswer(BaseModel):
    """Model for answers with exact quotes and source citations."""
    
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
