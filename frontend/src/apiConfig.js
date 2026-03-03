/**
 * Centralized API configuration for VerifiHireAI
 * This ensures that the frontend uses the correct API URL regardless of the environment.
 */

const getApiBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;

        // If we are in development (localhost/127.0.0.1)
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `http://${hostname}:8001/api`;
        }

        // If accessed via duckdns, Nginx handles the /api path.
        // We use the same protocol and hostname as the frontend.
        if (hostname === 'verifyhire.duckdns.org') {
            return `${protocol}//${hostname}/api`;
        }

        // Fallback for other domains
        return `${protocol}//${hostname}:8001/api`;
    }
    return process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';
};

const getWsBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `ws://${hostname}:8001/ws`;
        }

        if (hostname === 'verifyhire.duckdns.org') {
            // Nginx handles the /ws path
            return `${protocol}//${hostname}/ws`;
        }

        // Default for other domains
        return `${protocol}//${hostname}:8001/ws`;
    }
    return process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8001/ws';
};

export const API_BASE_URL = getApiBaseUrl();
export const WS_BASE_URL = getWsBaseUrl();

export default API_BASE_URL;
