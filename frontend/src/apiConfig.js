/**
 * Centralized API configuration for VerifiHireAI
 * Handles API + WebSocket URLs correctly for all environments
 */

const getApiBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;

        // ✅ LOCAL DEVELOPMENT
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `http://${hostname}:8001/api`;
        }

        // ✅ PRODUCTION (NGINX handles routing)
        if (hostname === 'verifihireai.com' || hostname === 'www.verifihireai.com') {
            return `${protocol}//${hostname}/api`;
        }

        // ✅ FALLBACK
        return `${protocol}//${hostname}:8001/api`;
    }

    return process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001/api';
};


const getWsBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        // ✅ LOCAL DEVELOPMENT
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `ws://${hostname}:8001/ws/interview`;
        }

        // ✅ PRODUCTION (NGINX handles /ws → backend)
        if (hostname === 'verifihireai.com' || hostname === 'www.verifihireai.com') {
            return `${protocol}//${hostname}/ws/interview`;
        }

        // ✅ FALLBACK
        return `${protocol}//${hostname}:8001/ws/interview`;
    }

    return process.env.REACT_APP_WS_BASE_URL || 'ws://localhost:8001/ws/interview';
};


export const API_BASE_URL = getApiBaseUrl();
export const WS_BASE_URL = getWsBaseUrl();

export default API_BASE_URL;