(function initialiseInterApi(global) {
  class ApiError extends Error {
    constructor(message, status = 0, details = null) {
      super(message);
      this.name = 'ApiError';
      this.status = status;
      this.details = details;
    }
  }

  class InterApiClient {
    constructor(config = {}) {
      this.baseUrl = String(config.apiBaseUrl || '/api/v1').replace(/\/$/, '');
      this.timeoutMs = Number(config.apiTimeoutMs || 4000);
    }

    async request(path, options = {}) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), this.timeoutMs);
      const headers = new Headers(options.headers || {});
      headers.set('Accept', 'application/json');
      if (options.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');

      try {
        const response = await fetch(`${this.baseUrl}${path}`, {
          ...options,
          headers,
          signal: controller.signal,
        });
        const contentType = response.headers.get('content-type') || '';
        const payload = contentType.includes('application/json') ? await response.json() : null;
        if (!response.ok) {
          const message = payload?.detail || `API request failed (${response.status})`;
          throw new ApiError(message, response.status, payload);
        }
        return payload;
      } catch (error) {
        if (error.name === 'AbortError') throw new ApiError('API request timed out');
        if (error instanceof ApiError) throw error;
        throw new ApiError('API is unavailable', 0, error);
      } finally {
        clearTimeout(timeout);
      }
    }

    health() { return this.request('/health/ready'); }
    listReels(scope, limit = 20) { return this.request(`/reels?scope=${encodeURIComponent(scope)}&limit=${limit}`); }
    getReel(id) { return this.request(`/reels/${encodeURIComponent(id)}`); }
    updateReel(id, payload) { return this.request(`/reels/${encodeURIComponent(id)}`, { method: 'PATCH', body: JSON.stringify(payload) }); }
    updateScript(id, payload) { return this.request(`/reels/${encodeURIComponent(id)}/script`, { method: 'PUT', body: JSON.stringify(payload) }); }
    listCompetitors(limit = 20) { return this.request(`/competitors?limit=${limit}`); }
    createCompetitor(payload) { return this.request('/competitors', { method: 'POST', body: JSON.stringify(payload) }); }
    getSettings() { return this.request('/settings'); }
    updateSettings(payload) { return this.request('/settings', { method: 'PATCH', body: JSON.stringify(payload) }); }
    getApifyConfiguration() { return this.request('/imports/apify/config'); }
    createApifyImport(payload) { return this.request('/imports/apify', { method: 'POST', body: JSON.stringify(payload) }); }
    getImport(id) { return this.request(`/imports/${encodeURIComponent(id)}`); }
  }

  global.InterApiError = ApiError;
  global.interApi = new InterApiClient(global.INTER_CONFIG || {});
})(window);

