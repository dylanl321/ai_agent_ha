// Global injection script for AI Agent HA FAB
// This script automatically injects the FAB on all pages

(function() {
  'use strict';

  // Wait for Home Assistant to be ready
  if (window.customElements && window.customElements.get('ai-agent-ha-fab')) {
    // Component already loaded, inject it
    injectFAB();
  } else {
    // Wait for component to be defined
    const checkInterval = setInterval(() => {
      if (window.customElements && window.customElements.get('ai-agent-ha-fab')) {
        clearInterval(checkInterval);
        injectFAB();
      }
    }, 100);

    // Timeout after 10 seconds
    setTimeout(() => clearInterval(checkInterval), 10000);
  }

  function injectFAB() {
    // Check if FAB already exists
    if (document.querySelector('ai-agent-ha-fab')) {
      return;
    }

    // Create and inject the FAB
    const fab = document.createElement('ai-agent-ha-fab');
    
    // Get Home Assistant object from the app
    const appEl = document.querySelector('home-assistant');
    if (appEl && appEl.hass) {
      fab.hass = appEl.hass;
      
      // Update hass when it changes
      const observer = new MutationObserver(() => {
        if (appEl.hass && fab.hass !== appEl.hass) {
          fab.hass = appEl.hass;
        }
      });
      
      observer.observe(appEl, {
        attributes: true,
        attributeFilter: ['hass']
      });
    }

    document.body.appendChild(fab);
  }

  // Also inject when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectFAB);
  } else {
    injectFAB();
  }
})();
