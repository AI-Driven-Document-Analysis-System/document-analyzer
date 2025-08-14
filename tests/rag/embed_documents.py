#!/usr/bin/env python3
"""
Simple Document Embedder for ChromaDB

Hardcode your document content here and run this script to embed it into ChromaDB.
No interactive prompts, just hardcoded content that gets processed and stored.
"""

import os
import sys
import uuid
from datetime import datetime

# Add the app directory to Python path (updated for new location)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from services.chatbot.vector_db.chunking import DocumentChunker
from services.chatbot.vector_db.indexing import LangChainDocumentIndexer
from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore


def get_documents():
    """Hardcode your documents here"""
    return [
        {
            'id': str(uuid.uuid4()),
            'type': 'policy',
            'filename': 'company_policy.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': 'admin',
            'text': """Company Policy Document

1. Introduction
This document outlines the company policies and procedures that all employees must follow.

2. Work Hours
Standard work hours are 9:00 AM to 5:00 PM Monday through Friday. Flexible scheduling may be available with manager approval.

3. Dress Code
Business casual attire is required. Jeans are permitted on Fridays. Please dress appropriately for client meetings.

4. Leave Policy
Employees are entitled to 20 days of paid leave per year. Leave requests must be submitted at least 2 weeks in advance.

5. Confidentiality
All company information must be kept confidential. Do not share sensitive information with unauthorized parties.

6. Internet Usage
Personal internet usage should be limited to breaks and lunch hours. Social media access is restricted during work hours.

7. Health and Safety
Report any safety concerns immediately to your supervisor. Regular safety training will be provided.

8. Conclusion
Following these policies ensures a productive and professional work environment for all employees."""
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'manual',
            'filename': 'software_manual.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': 'admin',
            'text': """Software User Manual

Getting Started
Welcome to our software application. This manual will guide you through the basic features and functionality.

Installation
1. Download the installer from our website
2. Run the installer as administrator
3. Follow the on-screen instructions
4. Restart your computer if prompted

First Launch
1. Open the application from your desktop or start menu
2. Enter your license key when prompted
3. Create your user account
4. Complete the initial setup wizard

Basic Features
- Document Management: Upload, organize, and search documents
- Text Analysis: Extract key information from documents
- Report Generation: Create detailed reports and summaries
- User Management: Manage user accounts and permissions

Advanced Features
- API Integration: Connect with external services
- Custom Workflows: Create automated document processing
- Analytics Dashboard: Monitor usage and performance
- Backup and Recovery: Protect your data

Troubleshooting
If you encounter issues:
1. Check the system requirements
2. Verify your internet connection
3. Restart the application
4. Contact technical support

Support
For additional help, visit our support portal or contact our technical team."""
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'report',
            'filename': 'quarterly_report.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': 'admin',
            'text': """Quarterly Business Report - Q4 2024

Executive Summary
This quarter showed strong performance across all business units with revenue growth of 15% compared to Q3.

Financial Performance
- Total Revenue: $2.5M (↑15% from Q3)
- Operating Expenses: $1.8M (↑8% from Q3)
- Net Profit: $700K (↑25% from Q3)
- Cash Flow: $500K positive

Key Achievements
1. Launched new product line with 20% market penetration
2. Expanded to 3 new geographic markets
3. Improved customer satisfaction score to 4.8/5.0
4. Reduced operational costs by 12%

Market Analysis
The market continues to show strong demand for our services. Competition remains moderate with no significant new entrants.

Challenges and Risks
- Supply chain disruptions affecting 15% of products
- Rising labor costs impacting margins
- Regulatory changes requiring compliance updates

Outlook for Q1 2025
We project continued growth with revenue targets of $2.8M. Focus areas include:
- Expanding product portfolio
- Improving operational efficiency
- Strengthening customer relationships

Recommendations
1. Invest in automation to reduce labor costs
2. Diversify supplier base to mitigate supply chain risks
3. Increase marketing budget for new product launch
4. Enhance employee training programs"""
        },{
            'id': str(uuid.uuid4()),
            'type': 'legal',
            'filename': 'data_protection_law_ocr.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': 'admin',
            'text': """CHAPTER III — OBLIGATIONS OF DATA CONTROLLERS

Sect1on 14. — Dutes Relatlng to LawfuI Processing

14(1) The Controler shall ensure that personaI data are processed fairIy, lawfuIIy
and in a transparant manner in relatlon to the Data SubJect. Such processing shalI
be undertaken only where one or more of the folIowing cond1tions are met:

(a) the Data Subject has given his/her freey given, speciflc, informed and unambigous consent;
(b) processing is necessary for the performance of a contract to which the Data Subject is a party;
(c) processing is necessary for compliance with a legal obl1gation to which the Controller is subject;
(d) processing is necessary to protect the vital interests of the Data Subject or of another natural person;
(e) processing is necessary for the performance of a task carried out in the publ1c interest or in the exercise of official authority vested in the Controller.

14(2) The Controller shaIl be responsibIe for, and be able to demonstrate, compliance
with paragraph (1) of this Sectlon.

Sectlon 15. — Informat1on to be Provided

15(1) Where personaI data relating to a Data Subject are collected from such subject,
the Controler shaII, at the t1me when personaI data are obta1ned, provide the data
subject with alI of the following informatlon:

(a) the identlty and the contact details of the Controller and, where applicable, of the Controller's representatlve;
(b) the contact detaIls of the data protection officer, where appllcable;
(c) the purposes of the processing for which the personaI data are intended as well as the legal basls for the processing;
(d) where the processing is based on point (a), the existence of the right to withdraw consent at any t1me, without affectlng the lawfulness of processing based on consent before its withdrawal."""
        }
        # ADD MORE DOCUMENTS HERE - just copy the format above
        # {
        #     'id': str(uuid.uuid4()),
        #     'type': 'your_doc_type',
        #     'filename': 'your_filename.txt',
        #     'upload_date': datetime.now().isoformat(),
        #     'user_id': 'admin',
        #     'text': """Your document content here..."""
        # },
    ]


def main():
    """Main function to embed documents"""
    print("🚀 Starting document embedding...")

    # Configuration
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_db')
    collection_name = "documents"

    try:
        # Initialize components
        vectorstore = LangChainChromaStore(db_path, collection_name)
        chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
        indexer = LangChainDocumentIndexer(vectorstore, chunker)

        print(f"✅ Initialized with ChromaDB at: {db_path}")
        print(f"✅ Collection: {collection_name}")

        # Get documents to embed
        documents = get_documents()
        print(f"📄 Found {len(documents)} documents to embed")

        # Process each document
        total_chunks = 0
        for i, doc in enumerate(documents, 1):
            print(f"\n🔄 Processing document {i}/{len(documents)}: {doc['filename']}")

            try:
                # Index the document
                chunk_ids = indexer.index_document(doc)
                total_chunks += len(chunk_ids)
                print(f"   ✅ Success! Created {len(chunk_ids)} chunks")

            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")

        print(f"\n🎉 Embedding complete!")
        print(f"   Documents processed: {len(documents)}")
        print(f"   Total chunks created: {total_chunks}")

        # Show collection info
        try:
            collection = vectorstore.client.get_collection(name=collection_name)
            count = collection.count()
            print(f"   ChromaDB collection count: {count}")
        except Exception as e:
            print(f"   Could not get collection count: {e}")

        print("\n✅ Your documents are now embedded in ChromaDB!")
        print("   You can now use them with your RAG pipeline and Gemini API.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure all dependencies are installed and the app directory structure is correct.")


if __name__ == "__main__":
    main()

