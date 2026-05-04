// Simple in-memory storage for the authentication access token
// This is more secure than localStorage against XSS attacks
let inMemoryToken = null;

export const setToken = (token) => {
  inMemoryToken = token;
};

export const getToken = () => {
  return inMemoryToken;
};

export const clearToken = () => {
  inMemoryToken = null;
};
