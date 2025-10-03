import React, { useEffect, useState } from 'react';

interface StorageData {
    totalStorage: number;
    usedStorage: number;
    availableStorage: number;
    usagePercentage: number;
}

export const StorageChart: React.FC = () => {
    const [storageData, setStorageData] = useState<StorageData | null>(null);
    const TOTAL_STORAGE = 5 * 1024 * 1024 * 1024; // 5GB

    useEffect(() => {
        const fetchStorageData = async () => {
            try {
                const response = await fetch('/api/analytics/document-uploads-over-time?period=30d');
                if (!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();

                const usedStorage = data.summary.totalSize || 0;
                setStorageData({
                    totalStorage: TOTAL_STORAGE,
                    usedStorage: usedStorage,
                    availableStorage: TOTAL_STORAGE - usedStorage,
                    usagePercentage: (usedStorage / TOTAL_STORAGE) * 100
                });
            } catch (error) {
                console.error('Error fetching storage data:', error);
            }
        };

        fetchStorageData();
    }, []);

    const formatBytes = (bytes: number) => {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Byte';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i)) + ' ' + sizes[i];
    };

    const percentage = storageData?.usagePercentage || 0;
    const radius = 80;
    const circumference = 2 * Math.PI * radius;
    const dashArray = circumference;
    const dashOffset = circumference * (1 - percentage / 100);

    return (
        <div style={{
            width: '300px',
            height: '350px',
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '20px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
            margin: '10px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            position: 'relative',
            border: '1px solid #e5e7eb'
        }}>
            <h3 style={{ 
                margin: '0 0 20px 0', 
                textAlign: 'center',
                fontSize: '18px',
                fontWeight: '600',
                color: '#111827'
            }}>
                Storage Usage
            </h3>
            <div style={{ 
                position: 'relative',
                width: '200px',
                height: '200px',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
            }}>
                <svg width="200" height="200" viewBox="0 0 200 200" style={{ transform: 'rotate(-90deg)' }}>
                    {/* Background circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        fill="none"
                        stroke="#E5E7EB"
                        strokeWidth="20"
                    />
                    {/* Progress circle */}
                    <circle
                        cx="100"
                        cy="100"
                        r={radius}
                        fill="none"
                        stroke="#4F46E5"
                        strokeWidth="20"
                        strokeLinecap="round"
                        strokeDasharray={dashArray}
                        strokeDashoffset={dashOffset}
                    />
                </svg>
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    textAlign: 'center',
                    fontSize: '24px',
                    fontWeight: 'bold',
                    color: '#4F46E5'
                }}>
                    {Math.round(percentage)}%
                </div>
            </div>
            <div style={{ 
                marginTop: '20px',
                textAlign: 'center',
                width: '100%'
            }}>
                <p style={{ 
                    margin: '0 0 10px 0',
                    fontSize: '14px',
                    color: '#6B7280'
                }}>
                    {`${formatBytes(storageData?.usedStorage || 0)} of ${formatBytes(storageData?.totalStorage || 0)} used`}
                </p>
                <div style={{ 
                    display: 'flex',
                    justifyContent: 'center',
                    gap: '16px',
                    fontSize: '14px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ 
                            width: '12px', 
                            height: '12px', 
                            backgroundColor: '#4F46E5', 
                            borderRadius: '50%' 
                        }} />
                        <span style={{ color: '#374151' }}>Used</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <div style={{ 
                            width: '12px', 
                            height: '12px', 
                            backgroundColor: '#E5E7EB', 
                            borderRadius: '50%' 
                        }} />
                        <span style={{ color: '#374151' }}>Available</span>
                    </div>
                </div>
            </div>
        </div>
    );
};
