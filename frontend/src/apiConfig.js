/**
 * Centralized API configuration for VerifiHireAI
 * This ensures that the frontend uses the correct API URL regardless of the environment.
 */

const getApiBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        // If accessed via custom host (like duckdns), Nginx proxies traffic on default ports
        // to port 8001, so we don't append the port here.
        if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
            return `${window.location.protocol}//${hostname}/api`;
        }
    }
    return process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';
};

const getWsBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        // Same as above, Nginx handles port proxying for external access
        if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
            return `${protocol}//${hostname}/ws`;
        }
    }
    // Fallback for local development
    return process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8001/ws';
};

export const API_BASE_URL = getApiBaseUrl();
export const WS_BASE_URL = getWsBaseUrl();

export default API_BASE_URL;
