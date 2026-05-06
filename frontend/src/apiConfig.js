/*
  Centralized API configuration for VerifiHireAI
 * Handles API + WebSocket URLs correctly for all environments
 */

const getApiBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;

        // ✅ LOCAL DEVELOPMENT
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `http://127.0.0.1:8001/api`;
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
            return `ws://127.0.0.1:8001/ws/interview`;
        }

        // ✅ PRODUCTION (NGINX handles /ws → backend)
        if (hostname === 'verifihireai.com' || hostname === 'www.verifihireai.com') {
            return `${protocol}//${hostname}/ws/interview`;
        }

        // ✅ FALLBACK
        return `${protocol}//${hostname}:8001/ws/interview`;
    }

    return process.env.REACT_APP_WS_BASE_URL || 'ws://127.0.0.1:8001/ws/interview';
};


const getDeepfaceBaseUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol;

        // ✅ LOCAL DEVELOPMENT
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `http://127.0.0.1:8500/api/v1`;
        }

        // ✅ PRODUCTION (NGINX proxies /deepface → deepface service)
        if (hostname === 'verifihireai.com' || hostname === 'www.verifihireai.com') {
            return `${protocol}//${hostname}/deepface/api/v1`;
        }

        // ✅ FALLBACK
        return `${protocol}//${hostname}:8500/api/v1`;
    }

    return process.env.REACT_APP_DEEPFACE_BASE_URL || 'http://localhost:8500/api/v1';
};

const getDeepfaceWsUrl = () => {
    if (typeof window !== 'undefined') {
        const hostname = window.location.hostname;
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

        // ✅ LOCAL DEVELOPMENT
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return `ws://127.0.0.1:8500/api/v1`;
        }

        // ✅ PRODUCTION
        if (hostname === 'verifihireai.com' || hostname === 'www.verifihireai.com') {
            return `${protocol}//${hostname}/deepface/api/v1`;
        }

        // ✅ FALLBACK
        return `${protocol}//${hostname}:8500/api/v1`;
    }

    return process.env.REACT_APP_DEEPFACE_WS_URL || 'ws://localhost:8500/api/v1';
};

export const API_BASE_URL = getApiBaseUrl();
export const WS_BASE_URL = getWsBaseUrl();
export const DEEPFACE_BASE_URL = getDeepfaceBaseUrl();
export const DEEPFACE_WS_URL = getDeepfaceWsUrl();

export default API_BASE_URL;