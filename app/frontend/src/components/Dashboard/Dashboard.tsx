import React from 'react';
import { StorageChart } from './StorageChart';

interface StorageData {
    totalStorage: number;
    usedStorage: number;
    availableStorage: number;
    usagePercentage: number;
}

const Dashboard: React.FC = () => {
    // Fixed hardcoded values
    const storageData: StorageData = {
        totalStorage: 2 * 1024 * 1024 * 1024, // 5GB
        usedStorage: 35 * 1024 * 1024, // 35MB
        availableStorage: (5 * 1024 * 1024 * 1024) - (35 * 1024 * 1024),
        usagePercentage: (35 * 1024 * 1024) / (5 * 1024 * 1024 * 1024) * 100
    };

    const formatBytes = (bytes: number) => {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Byte';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i)) + ' ' + sizes[i];
    };

    const percentage = storageData.usagePercentage;
    const radius = 80;
    const circumference = 2 * Math.PI * radius;
    const dashArray = circumference;
    const dashOffset = circumference * (1 - percentage / 100);

    return (
        <div className="dashboard-container">
            <div className="dashboard-grid" style={{ 
                display: 'grid',
                gap: '1rem',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                padding: '1rem'
            }}>
                <div className="dashboard-card">
                    <StorageChart />
                </div>
                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                    <p style={{ margin: '0.5rem 0' }}>
                        {`${formatBytes(storageData.usedStorage)} of ${formatBytes(storageData.totalStorage)} used`}
                    </p>
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '0.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <div style={{ width: '12px', height: '12px', backgroundColor: '#4F46E5', borderRadius: '50%' }} />
                            <span>Used</span>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                            <div style={{ width: '12px', height: '12px', backgroundColor: '#E5E7EB', borderRadius: '50%' }} />
                            <span>Available</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;