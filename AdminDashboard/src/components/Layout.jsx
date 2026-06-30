import React from 'react';
import Sidebar from './Sidebar';
import Header from './Header';

function Layout({ children }) {
    return (
        <div style={{
            display: 'flex',
            minHeight: '100vh',
            background: 'var(--bg-main)',
            fontFamily: "'DM Sans', sans-serif"
        }}>
            <Sidebar />
            <div style={{
                flex: 1,
                marginLeft: 280,
                display: 'flex',
                flexDirection: 'column',
                minWidth: 0 // Prevent flex children from overflowing
            }}>
                <Header />
                <main style={{
                    padding: '30px',
                    flex: 1,
                    maxWidth: '1600px', // Limit width on very large screens for readability
                    width: '100%',
                    margin: '0 auto'
                }}>
                    {children}
                </main>
            </div>
        </div>
    );
}

export default Layout;
