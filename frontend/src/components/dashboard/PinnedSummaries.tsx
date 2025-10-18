// import React from 'react';

// interface Summary {
//   id: string;
//   title: string;
//   document: string;
//   created_at: string;
// }

// const PinnedSummaries: React.FC = () => {
//   // Hardcoded fake summaries
//   const summaries: Summary[] = [
//     {
//       id: '1',
//       title: 'Q4 Financial Report Analysis',
//       document: 'financial_report_2024.pdf',
//       created_at: '2025-10-15T10:30:00Z'
//     },
//     {
//       id: '2',
//       title: 'Market Research Key Findings',
//       document: 'market_analysis.docx',
//       created_at: '2025-10-14T15:45:00Z'
//     },
//     {
//       id: '3',
//       title: 'Product Roadmap Overview',
//       document: 'roadmap_2025.pdf',
//       created_at: '2025-10-13T09:20:00Z'
//     }
//   ];

//   const formatDate = (dateString: string) => {
//     const date = new Date(dateString);
//     const now = new Date();
//     const diffMs = now.getTime() - date.getTime();
//     const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    
//     if (diffHours < 1) return 'Just now';
//     if (diffHours < 24) return `${diffHours}h ago`;
//     const diffDays = Math.floor(diffHours / 24);
//     if (diffDays < 7) return `${diffDays}d ago`;
//     return date.toLocaleDateString();
//   };

//   return (
//     <div className="feature-container" style={{ flex: '1', marginTop: '1.5rem' }}>
//       <div className="tab-content-container">
//         <h5 className="mb-4"><i className="fas fa-bookmark me-2"></i>Pinned Summaries</h5>

//         <div>
//           {summaries.map((summary) => (
//             <div 
//               key={summary.id} 
//               className="result-item"
//             >
//               <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
//                 <div className="flex-grow-1">
//                   <div className="result-title" style={{ marginBottom: '0.5rem' }}>
//                     {summary.title}
//                   </div>
//                   <div className="result-meta">
//                     {summary.document} • {formatDate(summary.created_at)}
//                   </div>
//                 </div>
//                 <button
//                   onClick={() => console.log('View summary:', summary.id)}
//                   style={{
//                     padding: '6px 12px',
//                     fontSize: '0.75rem',
//                     fontWeight: 500,
//                     backgroundColor: '#10b981',
//                     color: 'white',
//                     border: 'none',
//                     borderRadius: '6px',
//                     cursor: 'pointer',
//                     transition: 'all 0.2s ease',
//                     whiteSpace: 'nowrap'
//                   }}
//                   onMouseEnter={(e) => e.currentTarget.style.backgroundColor = '#059669'}
//                   onMouseLeave={(e) => e.currentTarget.style.backgroundColor = '#10b981'}
//                 >
//                   View Summary
//                 </button>
//               </div>
//             </div>
//           ))}
//         </div>
//       </div>
//     </div>
//   );
// };

// export default PinnedSummaries;


import React from 'react';

const PinnedSummaries: React.FC = () => {
  return (
    <div className="feature-container" style={{ flex: '1', marginTop: '1.5rem' }}>
      <div className="tab-content-container" style={{
        backgroundColor: 'var(--bg-primary)',
        borderRadius: '8px',
        boxShadow: 'var(--card-shadow)',
        padding: '24px',
        border: '1px solid var(--border-color)',
        textAlign: 'center',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '200px'
      }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '12px', color: 'var(--text-tertiary)' }}>
          <i className="fas fa-bookmark"></i>
        </div>
        <h5 style={{ 
          fontSize: '1.1rem', 
          fontWeight: '600', 
          color: 'var(--text-primary)', 
          marginBottom: '8px',
          margin: '0 0 8px 0'
        }}>
          No Pinned Summaries
        </h5>
        <p style={{ 
          color: 'var(--text-secondary)', 
          fontSize: '0.9rem', 
          margin: 0 
        }}>
          Pin your favorite summaries to access them here
        </p>
      </div>
    </div>
  );
};

export default PinnedSummaries;