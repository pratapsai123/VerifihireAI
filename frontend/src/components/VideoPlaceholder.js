import React from 'react';

const VideoPlaceholder = ({ name, width = '100%', height = '100%', style = {} }) => {
    return (
        <div
            style={{
                width: width,
                height: height,
                backgroundColor: '#1a1a1a', // Dark background
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#ffffff',
                position: 'relative',
                ...style
            }}
        >
            <div style={{
                width: '80px',
                height: '80px',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem',
                border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    style={{ width: '40px', height: '40px', opacity: 0.5 }}
                >
                    <path
                        fillRule="evenodd"
                        d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z"
                        clipRule="evenodd"
                    />
                </svg>
            </div>
            {name && (
                <span style={{ fontSize: '1rem', fontWeight: 500, color: 'rgba(255, 255, 255, 0.7)', textAlign: 'center', padding: '0 10px' }}>
                    {name}
                </span>
            )}
        </div>
    );
};

export default VideoPlaceholder;
