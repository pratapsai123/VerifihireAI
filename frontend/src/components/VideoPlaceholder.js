import React from 'react';

const VideoPlaceholder = ({ name, width = '100%', height = '100%', style = {} }) => {
    return (
        <div
            style={{
                width: width,
                height: height,
                backgroundColor: '#e5e7eb', // gray-200
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#9ca3af', // gray-400
                ...style
            }}
        >
            <div style={{
                width: '120px',
                height: '120px',
                backgroundColor: '#f3f4f6', // gray-100
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: '1rem'
            }}>
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 24 24"
                    fill="currentColor"
                    style={{ width: '80px', height: '80px' }}
                >
                    <path
                        fillRule="evenodd"
                        d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z"
                        clipRule="evenodd"
                    />
                </svg>
            </div>
            {name && (
                <span style={{ fontSize: '1.25rem', fontWeight: 600, color: '#4b5563' }}>
                    {name}
                </span>
            )}
        </div>
    );
};

export default VideoPlaceholder;
