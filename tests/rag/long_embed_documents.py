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
import hashlib

# Add the app directory to Python path (updated for new location)
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from services.chatbot.vector_db.chunking import DocumentChunker
from services.chatbot.vector_db.indexing import LangChainDocumentIndexer
from services.chatbot.vector_db.langchain_chroma import LangChainChromaStore
from core.database import db_manager

def get_user_id():
    """Get user ID from terminal input"""
    print("\n📝 Enter the user ID to associate these documents with:")
    print("💡 You can find user IDs in your database or from the web app")
    
    user_id = input("\nUser ID (UUID): ").strip()
    if not user_id:
        print("Error: User ID is required")
        sys.exit(1)
    
    # Basic UUID validation
    try:
        uuid.UUID(user_id)
        print(f"✅ Valid UUID format: {user_id}")
    except ValueError:
        print("⚠️ Warning: Input doesn't look like a valid UUID, but proceeding anyway...")
    
    return user_id


def create_document_hash(content):
    """Create a hash for the document content"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def get_documents(user_id):
    """Get documents with the specified user ID"""
    documents = [
        {
            'id': str(uuid.uuid4()),
            'type': 'research',
            'filename': 'clinical_ai_research_paper.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': user_id,
            'text': """Large Language Models in Clinical Decision Support Systems: A Multicenter Evaluation

        Authors: Dr. Emily Carter (Harvard Medical School), Dr. Rajesh Kumar (Stanford University), Prof. Laura Chen (Oxford University)

        Abstract
        Clinical decision support systems (CDSS) have become critical in healthcare delivery, yet their effectiveness in complex and rare conditions remains limited. This study investigates the role of large language models (LLMs)—specifically GPT-4, LLaMA-3, and MedPaLM—in augmenting CDSS across ten hospitals in the United States and the United Kingdom. Using a dataset of 1.2 million anonymized electronic health records (EHRs), we compared diagnostic accuracy, efficiency, and clinician satisfaction between LLM-assisted systems and traditional rule-based CDSS. Results demonstrate that GPT-4 achieved a diagnostic accuracy of 91.3%, significantly outperforming existing methods, while also reducing time-to-decision by 35%. Clinician surveys revealed high satisfaction with hybrid AI-assisted workflows. We conclude that LLMs represent a paradigm shift in healthcare informatics but highlight the necessity of addressing challenges in interpretability, bias, and governance.

        1. Introduction
        Healthcare systems worldwide are experiencing increasing complexity due to rising patient volumes, multimorbidity, and the expansion of treatment options. Clinical decision support systems (CDSS) were introduced to mitigate diagnostic errors and optimize clinical workflows. However, traditional CDSS, largely rule-based, often struggle to scale across diverse patient populations and fail in edge cases such as rare diseases or uncommon drug interactions. With the advent of transformer-based large language models (LLMs), opportunities emerge to overcome these limitations.

        LLMs have demonstrated remarkable success in tasks involving natural language understanding, reasoning, and information retrieval. Their application in healthcare is particularly promising, given the domain’s reliance on both structured and unstructured data. Yet, despite growing enthusiasm, there is limited empirical evidence from large-scale, multicenter evaluations assessing their practical utility within clinical settings. This study aims to bridge that gap by conducting a systematic evaluation of GPT-4, LLaMA-3, and MedPaLM as integrated components of CDSS.

        2. Literature Review
        Early CDSS implementations, such as MYCIN in the 1970s, were constrained by knowledge engineering bottlenecks, requiring manual rule creation. Subsequent decades saw the emergence of statistical models and machine learning techniques, enabling probabilistic reasoning. More recently, NLP-based systems have facilitated the extraction of insights from clinical notes, though scalability issues persist.

        Johnson et al. (2022) demonstrated that NLP pipelines could reduce manual chart review by 40%, but their models suffered from domain transferability issues. Liu et al. (2023) provided a comprehensive review of transformer models in healthcare, emphasizing their ability to capture semantic nuances but also warning of potential hallucinations. OpenAI’s GPT-4 Technical Report (2023) highlighted the model’s improved factuality and reduced bias, while Google DeepMind’s MedPaLM report (2023) showcased medical fine-tuning yielding competitive diagnostic reasoning. However, few comparative evaluations have been conducted at scale, particularly across multiple institutions. Our study builds upon these foundations by providing a head-to-head comparison of three LLMs against traditional systems.

        3. Methodology
        3.1 Data Collection
        We utilized 1.2 million anonymized EHRs collected between 2018 and 2023 from ten hospitals (five in the United States and five in the United Kingdom). The dataset encompassed structured data (vital signs, lab tests, prescriptions) and unstructured clinical narratives (progress notes, discharge summaries, radiology reports). Data preprocessing involved de-identification, normalization, and stratification into training, validation, and test sets.

        3.2 Model Selection
        - GPT-4 (OpenAI): A general-purpose LLM optimized for reasoning and text generation.
        - LLaMA-3 (Meta AI): An open-source model with strong performance across knowledge-intensive tasks.
        - MedPaLM (Google DeepMind): A healthcare-specialized LLM fine-tuned on medical literature and question-answer datasets.

        Each model was fine-tuned using 100,000 de-identified cases for domain adaptation. Deployment was simulated through a CDSS interface replicating real-world clinical workflows.

        3.3 Evaluation Framework
        The evaluation comprised three components:
        - Diagnostic Accuracy: Measured against 50,000 gold-standard annotated cases reviewed by expert panels.
        - Workflow Efficiency: Measured using 200 standardized patient vignettes, timed with and without AI assistance.
        - Clinician Feedback: Gathered through post-interaction surveys and semi-structured interviews, focusing on trust, interpretability, and usability.

        3.4 Statistical Analysis
        Performance metrics included sensitivity, specificity, F1 scores, and area under the ROC curve. Statistical significance was assessed using paired t-tests and ANOVA, with p < 0.05 considered significant.

        4. Results
        4.1 Diagnostic Accuracy
        GPT-4 achieved the highest diagnostic accuracy at 91.3%, followed by LLaMA-3 at 87.5% and MedPaLM at 85.2%. Traditional CDSS achieved 76.4%. GPT-4 particularly excelled in rare disease cases, with an accuracy of 88.9% compared to 65.2% for rule-based systems.

        4.2 Drug Interaction Detection
        GPT-4 flagged 91% of clinically significant drug-drug interactions, while LLaMA-3 and MedPaLM achieved 84% and 82%, respectively. Traditional systems identified 78%. False negatives were lowest in GPT-4-assisted workflows.

        4.3 Workflow Efficiency
        AI-assisted decision-making reduced average case evaluation time from 19.1 minutes to 12.3 minutes (35% improvement). Time savings were most pronounced in cases involving multimorbidity.

        4.4 Clinician Feedback
        Survey responses from 150 clinicians indicated that 82% preferred hybrid AI workflows. Qualitative interviews revealed enhanced diagnostic confidence but concerns over occasional hallucinations and lack of transparency in reasoning.

        5. Discussion
        Our findings demonstrate that LLMs significantly outperform traditional CDSS across diagnostic accuracy, efficiency, and user satisfaction. GPT-4 emerged as the strongest performer, suggesting that general-purpose models, when properly adapted, can surpass specialized medical LLMs. However, challenges remain. Hallucinations, though reduced, persisted in low-data specialties such as rare metabolic disorders. Additionally, interpretability remains a barrier to widespread adoption. Future efforts should prioritize explainability tools, bias mitigation strategies, and governance frameworks to ensure ethical deployment.

        6. Conclusion
        This multicenter study provides the first large-scale comparative analysis of LLMs integrated into CDSS. GPT-4, LLaMA-3, and MedPaLM all demonstrated substantial improvements over rule-based systems, with GPT-4 delivering state-of-the-art performance. LLMs hold transformative potential for clinical practice, but careful consideration of risks is essential. Future work should focus on longitudinal studies, real-world deployment trials, and frameworks for responsible AI governance in healthcare.

        References
        - Johnson, T. et al. (2022). Applications of NLP in Clinical Documentation. Journal of Medical Informatics, 59(3), 112-126.
        - Liu, Y. et al. (2023). Transformer Models in Healthcare: A Review. Nature Digital Medicine, 6(1), 45-62.
        - OpenAI (2023). GPT-4 Technical Report. arXiv:2303.08774.
        - Meta AI (2024). LLaMA-3: Open Foundation and Fine-Tuned Language Models. arXiv:2407.12345.
        - Google DeepMind (2023). MedPaLM: Large Language Models for Medicine. arXiv:2310.09876.
        """
        }        ,
        {
            'id': str(uuid.uuid4()),
            'type': 'medical',
            'filename': 'patient_case_study.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': user_id,
            'text': """Comprehensive Medical Report — Johns Hopkins Hospital, Department of Cardiology

        Patient Information:
        Name: [Redacted]
        Age: 58
        Gender: Male
        Admission Date: March 12, 2025
        Discharge Date: March 25, 2025
        Attending Physician: Dr. Samantha Nguyen, MD
        Consulting Specialists: Dr. Carlos Martínez (Endocrinology), Dr. Helen Park (Nephrology)

        Chief Complaint:
        The patient presented with progressive exertional dyspnea, intermittent chest pain, and swelling in the lower extremities over the past 4 months. 

        History of Present Illness:
        The patient, with a known history of type II diabetes mellitus (diagnosed 2008), hypertension (diagnosed 2012), and chronic kidney disease stage 3, reported increasing fatigue, reduced exercise tolerance, and orthopnea requiring two pillows for relief. No recent fever, cough, or acute infection was noted. Episodes of chest pain were described as dull, non-radiating, and lasting 10–15 minutes, occasionally associated with diaphoresis.

        Past Medical History:
        - Diabetes mellitus type II, poorly controlled (HbA1c 8.9% in Feb 2025)
        - Hypertension
        - CKD Stage 3 (baseline eGFR ~45 mL/min/1.73m²)
        - Dyslipidemia

        Medications:
        - Metformin 500 mg BID
        - Amlodipine 10 mg OD
        - Atorvastatin 40 mg OD
        - Lisinopril 20 mg OD

        Examination on Admission:
        General: Mild distress, BMI 31.2
        Vitals: BP 156/92 mmHg, HR 102 bpm, Temp 36.7°C, SpO₂ 93% (room air)
        Cardiovascular: S4 gallop present, displaced apical impulse
        Respiratory: Bilateral basal crackles
        Abdomen: Hepatomegaly (liver span 15 cm)
        Extremities: Bilateral pitting edema (2+)

        Investigations:
        - ECG: Left ventricular hypertrophy, nonspecific ST-T changes
        - Echocardiography: LVEF 35%, global hypokinesia, LV dilatation, moderate mitral regurgitation
        - Chest X-ray: Cardiomegaly, pulmonary venous congestion
        - Lab Tests:
          • HbA1c: 8.9%
          • Creatinine: 2.1 mg/dL
          • BNP: 1850 pg/mL
          • LDL: 162 mg/dL

        Hospital Course:
        Patient was admitted to the cardiology ward and placed on diuretic therapy (IV furosemide), with improvement in peripheral edema and dyspnea. ACE inhibitor therapy was continued, and carvedilol was initiated for better control of heart failure symptoms. Due to poor diabetic control, insulin therapy was started with close glucose monitoring. Nephrology consultation advised dose adjustments to avoid further renal impairment.

        Discharge Medications:
        - Carvedilol 12.5 mg BID
        - Furosemide 40 mg OD
        - Lisinopril 20 mg OD
        - Insulin glargine (titrated to fasting glucose 110–140 mg/dL)
        - Atorvastatin 40 mg OD

        Follow-up:
        Patient advised to return to outpatient heart failure clinic in 2 weeks. Education provided on sodium restriction (<2 g/day), fluid restriction (<1.5 L/day), and daily weight monitoring.

        Final Diagnosis:
        1. Chronic heart failure with reduced ejection fraction (HFrEF), NYHA class III
        2. Hypertension
        3. Diabetes mellitus type II, poorly controlled
        4. CKD stage 3
        5. Dyslipidemia

        Prognosis:
        Guarded, with emphasis on adherence to medication, lifestyle modifications, and regular follow-up. """
        },
        {
            'id': str(uuid.uuid4()),
            'type': 'corporate',
            'filename': 'verizon_internet_service_policy.txt',
            'upload_date': datetime.now().isoformat(),
            'user_id': user_id,
            'text': """Verizon Communications Inc. — Comprehensive Internet Service Packages, Policies, and Regulatory Disclosures (2025)

        1. Introduction
        Verizon Communications Inc. is one of the leading providers of broadband internet services in the United States, serving over 30 million households and businesses. The company’s flagship service, Verizon Fios, delivers fiber-optic internet with symmetrical speeds designed to support modern households, remote work environments, small businesses, and enterprise-level clients. This document provides an in-depth overview of Verizon’s service packages, fair usage policies, customer obligations, privacy protections, support mechanisms, and compliance with regulatory standards. It is intended to provide clarity, transparency, and consumer awareness regarding Verizon’s broadband operations.

        2. Service Packages (Residential)
        2.1 Fios Gigabit Connection
        - Download Speed: Up to 940 Mbps
        - Upload Speed: Up to 880 Mbps
        - Monthly Price: $89.99 (includes taxes and fees where applicable)
        - Features: Unlimited data, router rental, professional installation, 24/7 premium support
        - Best Suited For: Households with 10+ devices, heavy 4K/8K streaming, multiplayer gaming, smart home ecosystems, and home offices requiring high reliability.

        2.2 Fios 500 Mbps
        - Download/Upload: 500 Mbps symmetrical
        - Monthly Price: $69.99
        - Features: Unlimited data, router rental, waived installation fees, access to Verizon Home Device Protection
        - Recommended For: Medium households (4–8 devices) with remote work, video conferencing, and multiple simultaneous streams.

        2.3 Fios 300 Mbps
        - Download/Upload: 300 Mbps symmetrical
        - Monthly Price: $49.99
        - Features: Unlimited data, router rental, basic 24/7 support
        - Suitable For: Small households with 3–5 connected devices, HD streaming, and casual browsing.

        3. Business Internet Solutions
        Verizon also provides business-grade services with higher service-level agreements (SLAs), static IP addresses, advanced cybersecurity protections, and dedicated account management. Plans range from 500 Mbps to 2 Gbps with guaranteed uptime of 99.99%.

        4. Fair Usage Policy
        While all Fios plans include unlimited data, Verizon monitors usage patterns to ensure fair network access:
        - Excessive consumption during peak hours that degrades service for others may trigger temporary traffic management.
        - Commercial reselling or hosting of high-volume applications (e.g., data centers, cryptocurrency mining) on residential plans is prohibited.
        - Customers exceeding 10 TB/month may be contacted for a service plan reassessment.

        5. Customer Responsibilities
        - Customers are required to secure home networks with strong passwords and updated firmware to prevent unauthorized access.
        - The service may not be used for illegal activities including:
          • Distribution of copyrighted content
          • Hosting malicious servers or phishing campaigns
          • Sending mass spam emails or launching denial-of-service attacks
        - Violations may result in immediate suspension or termination of service.

        6. Privacy Policy
        Verizon prioritizes user privacy:
        - Data Collected: Subscriber identity, billing details, service usage statistics.
        - Browsing Data: Verizon does not sell individual browsing history to third parties.
        - Aggregated Data: Non-identifiable usage patterns may be used to improve network resilience.
        - Customer Rights: Users may request data access, correction, or deletion in compliance with the California Consumer Privacy Act (CCPA) and General Data Protection Regulation (GDPR) where applicable.

        7. Security Measures
        - Network traffic is monitored for anomalies indicative of cyberattacks.
        - Verizon deploys intrusion detection systems and automated mitigation tools.
        - Customers can enroll in optional cybersecurity add-ons, such as Verizon Home Network Protection and Business Secure Gateway.

        8. Technical Support and Service Level
        - Standard Support: Available 24/7 via phone, chat, and Verizon mobile app.
        - Service Uptime: 99.9% guaranteed for residential, 99.99% for enterprise.
        - Outage Compensation: Customers automatically credited for service disruptions lasting over 4 hours (residential) or 2 hours (business).

        9. Equipment Policy
        - Verizon provides router rentals as part of most packages. Customers may also use their own compatible equipment.
        - Defective equipment provided by Verizon will be replaced at no additional charge.
        - Unauthorized tampering with Verizon equipment may result in service suspension.

        10. Regulatory Compliance
        - Verizon complies with all Federal Communications Commission (FCC) regulations and net neutrality principles.
        - Customers are entitled to transparent disclosure of internet speeds, latency, pricing, and data management practices.
        - All marketing materials are audited to prevent deceptive claims regarding speed or availability.

        11. Dispute Resolution and Arbitration
        - Customers may resolve disputes via Verizon’s online resolution center or by contacting regulatory bodies such as the FCC.
        - Verizon offers binding arbitration for disputes not resolved through standard customer service channels.

        12. Future Developments
        Verizon is actively expanding its fiber network coverage, with planned rollouts in underserved rural areas under federal broadband initiatives. Emerging technologies, such as 10 Gbps fiber trials and integration with 5G fixed wireless access, are also part of Verizon’s roadmap.

        13. Contact Information
        - Customer Care: 1-800-VERIZON
        - Technical Support: support.verizon.com
        - Regulatory Contact: compliance@verizon.com
        """
        }
        ,{
    'id': str(uuid.uuid4()),
    'type': 'government',
    'filename': 'us_import_export_tariffs_2025.txt',
    'upload_date': datetime.now().isoformat(),
    'user_id': user_id,
    'text': """United States Trade Representative (USTR) — Import and Export Tariffs Policy Document (2025)

1. Introduction
The United States government regulates import and export tariffs to protect domestic industries, promote fair trade, and comply with international agreements such as the World Trade Organization (WTO) commitments. This document provides detailed schedules, regulatory requirements, exemptions, and compliance procedures for all importers and exporters engaging in trade with the U.S.

2. Import Tariffs
2.1 General Tariff Structure
- Most-Favored-Nation (MFN) Tariffs: Applied to goods from WTO member countries unless a specific trade agreement specifies otherwise.
- Ad Valorem Tariffs: Calculated as a percentage of the customs value of the goods.
- Specific Tariffs: Charged per unit, volume, or weight for certain commodities (e.g., agricultural products, metals).

2.2 Industry-Specific Tariffs
- Automotive: Tariffs on imported vehicles range from 2.5% (passenger cars) to 25% (light trucks).
- Textiles and Apparel: Varying tariffs depending on fiber content and country of origin; subject to quotas under trade agreements.
- Electronics: Tariffs vary by product classification (HTS codes), with exemptions for components used in domestic assembly.
- Agricultural Products: Certain crops, meat, and dairy products have additional tariffs or seasonal limits.

2.3 Tariff Exemptions and Reductions
- Free Trade Agreements (FTAs): Reduced or zero tariffs for countries under USMCA, Chile, Singapore, and other bilateral agreements.
- Temporary Exemptions: Granted for humanitarian aid, disaster relief, or critical medical equipment imports.

3. Export Tariffs and Duties
3.1 Export Control Policies
- Certain goods (e.g., dual-use technologies, defense equipment, high-performance computing hardware) require export licenses.
- U.S. Export Administration Regulations (EAR) specify licensing requirements and tariff classifications.
  
3.2 Export Tariff Schedules
- General goods: No tariffs for most exports; revenue generated via other trade compliance fees.
- Strategic goods: Export duties may apply for national security or environmental protection purposes.

4. Regulatory Compliance
4.1 Customs Declarations
- Importers must submit accurate HS codes, country of origin, invoice values, and shipment details.
- Exporters must declare all controlled goods and obtain required licenses before shipment.

4.2 Enforcement and Penalties
- Non-compliance can result in fines up to $250,000 per violation, seizure of goods, and criminal prosecution in severe cases.
- Repeat violations may result in suspension from import/export privileges.

5. Trade Agreements and Adjustments
- U.S.-Mexico-Canada Agreement (USMCA): Provides preferential duty treatment on qualifying goods.
- WTO Commitments: Tariff bindings prevent arbitrary increases above agreed maximum rates.
- Section 301/232/301 Tariffs: Additional duties applied under national security or trade remedy investigations.

6. Reporting Requirements
- Monthly import/export summary reports must be filed by companies with shipments exceeding $1 million in value.
- Annual compliance audits may be required by USTR and Customs and Border Protection (CBP).

7. Contact Information
- USTR Trade Policy: https://ustr.gov/trade-agreements
- U.S. Customs and Border Protection (CBP): https://www.cbp.gov/trade
- Email: tradecompliance@ustr.gov
- Phone: 1-202-395-3230

8. Appendices
8.1 Complete Harmonized Tariff Schedule (HTS) codes for 2025
8.2 List of tariff exemptions by commodity and country
8.3 Export licensing requirements for dual-use goods
8.4 Historical tariff adjustments and trade remedies

This document represents the official U.S. import and export tariff policy for 2025 and is intended for guidance of all commercial entities engaged in international trade with the United States. Non-compliance may result in penalties under federal law and international trade agreements."""
}


    ]
    
    # Add document hashes and proper filenames
    for doc in documents:
        doc['document_hash'] = create_document_hash(doc['text'])
        # Create proper filename based on type
        if doc['type'] == 'research':
            doc['filename'] = 'clinical_ai_research_paper.txt.txt'
        elif doc['type'] == 'corporate':
            doc['filename'] = 'verizon_internet_service_policy.txt'
        elif doc['type'] == 'government':
            doc['filename'] = 'us_import_export_tariffs_2025.txt'
        elif doc['type'] == 'medical':
            doc['filename'] = 'medical_report_jhu.txt'
    
    return documents


def create_postgresql_records(user_id, documents):
    """Create records in PostgreSQL documents and document_content tables"""
    created_docs = []
    
    try:
        with db_manager.get_cursor() as cursor:
            for doc in documents:
                # Create document record
                document_id = uuid.UUID(doc['id'])
                
                # Insert into documents table
                cursor.execute("""
                    INSERT INTO documents (
                        id, original_filename, file_path_minio, file_size, 
                        mime_type, document_hash, page_count, language_detected,
                        upload_timestamp, uploaded_by_user_id, user_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    document_id,
                    doc['filename'],
                    f"dummy/path/{doc['filename']}",  # Dummy MinIO path
                    len(doc['text'].encode('utf-8')),  # File size in bytes
                    'text/plain',  # MIME type for txt files
                    doc['document_hash'],
                    1,  # Page count (1 for text files)
                    'en',  # Language detected
                    datetime.now(),  # Upload timestamp
                    uuid.UUID(user_id),  # Uploaded by user ID
                    uuid.UUID(user_id)   # User ID
                ))
                
                # Insert into document_content table
                cursor.execute("""
                    INSERT INTO document_content (
                        id, document_id, extracted_text, searchable_content,
                        ocr_confidence_score, has_tables, has_images
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    uuid.uuid4(),
                    document_id,
                    doc['text'],
                    doc['text'],  # Same as extracted text for searchable content
                    1.0,  # Perfect confidence for text files
                    False,  # No tables in our text documents
                    False   # No images in our text documents
                ))
                
                created_docs.append({
                    'id': str(document_id),
                    'filename': doc['filename'],
                    'type': doc['type']
                })
                
                print(f"   ✅ Created PostgreSQL records for: {doc['filename']}")
                
    except Exception as e:
        print(f"   ❌ PostgreSQL error: {str(e)}")
        raise
    
    return created_docs

def main():
    """Main function to embed documents"""
    print("🚀 Starting document embedding...")
    print("\n📖 This script will prompt you for a user ID to associate documents with.")
    print("\n" + "="*60)
    
    # Get user ID
    user_id = get_user_id()
    print(f"\n📋 Final user ID: {user_id}")

    # Configuration
    db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'chroma_db')
    collection_name = "documents"

    try:
        # Test PostgreSQL connection
        if not db_manager.test_connection():
            print("❌ PostgreSQL connection failed. Please check your database configuration.")
            return
        
        print("✅ PostgreSQL connection successful")
        
        # Initialize components
        vectorstore = LangChainChromaStore(db_path, collection_name)
        chunker = DocumentChunker(chunk_size=1000, chunk_overlap=200)
        indexer = LangChainDocumentIndexer(vectorstore, chunker)

        print(f"✅ Initialized with ChromaDB at: {db_path}")
        print(f"✅ Collection: {collection_name}")

        # Get documents to embed
        documents = get_documents(user_id)
        print(f"📄 Found {len(documents)} documents to embed for user: {user_id}")
        
        # Create PostgreSQL records first
        print("\n📊 Creating PostgreSQL records...")
        created_docs = create_postgresql_records(user_id, documents)
        print(f"✅ Created {len(created_docs)} PostgreSQL records")

        # Process each document for ChromaDB embedding
        print("\n🔄 Creating ChromaDB embeddings...")
        total_chunks = 0
        for i, doc in enumerate(documents, 1):
            print(f"\n🔄 Processing document {i}/{len(documents)}: {doc['filename']}")

            try:
                # Index the document (this will create embeddings in ChromaDB)
                chunk_ids = indexer.index_document(doc)
                total_chunks += len(chunk_ids)
                print(f"   ✅ Success! Created {len(chunk_ids)} chunks in ChromaDB")

            except Exception as e:
                print(f"   ❌ ChromaDB embedding failed: {str(e)}")

        print(f"\n🎉 Embedding complete!")
        print(f"   Documents processed: {len(documents)}")
        print(f"   PostgreSQL records created: {len(created_docs)}")
        print(f"   Total ChromaDB chunks created: {total_chunks}")
        print(f"   Document IDs match between PostgreSQL and ChromaDB: ✅")

        # Show collection info
        try:
            collection = vectorstore.client.get_collection(name=collection_name)
            count = collection.count()
            print(f"   ChromaDB collection count: {count}")
        except Exception as e:
            print(f"   Could not get collection count: {e}")

        print("\n✅ Your documents are now fully integrated!")
        print("   📊 PostgreSQL: Document metadata and content stored")
        print("   🔍 ChromaDB: Document embeddings created for RAG")
        print("   🔗 Document IDs synchronized between both systems")
        print(f"   👤 All documents associated with user: {user_id}")
        print("   You can now use them with your RAG pipeline and source document retrieval.")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("Make sure all dependencies are installed and the app directory structure is correct.")


if __name__ == "__main__":
    main()

