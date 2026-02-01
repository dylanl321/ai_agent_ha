// Lovelace Card for AI Agent HA - Can be added to any dashboard
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class AiAgentHaCard extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      config: { type: Object },
      _messages: { type: Array },
      _isLoading: { type: Boolean },
      _inputValue: { type: String },
    };
  }

  static get styles() {
    return css`
      :host {
        display: block;
      }

      .card {
        background: var(--card-background-color, #fff);
        border-radius: var(--ha-card-border-radius, 12px);
        box-shadow: var(--ha-card-box-shadow, none);
        padding: 16px;
        display: flex;
        flex-direction: column;
        height: 100%;
        min-height: 400px;
      }

      .header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
      }

      .header ha-icon {
        color: var(--primary-color, #03a9f4);
      }

      .header h2 {
        margin: 0;
        font-size: 18px;
        font-weight: 500;
        flex: 1;
      }

      .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 12px 0;
        display: flex;
        flex-direction: column;
        gap: 12px;
        min-height: 200px;
      }

      .message {
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 85%;
        word-wrap: break-word;
        font-size: 14px;
        line-height: 1.4;
      }

      .message.user {
        align-self: flex-end;
        background: var(--primary-color, #03a9f4);
        color: white;
      }

      .message.assistant {
        align-self: flex-start;
        background: var(--secondary-background-color, #f5f5f5);
        color: var(--primary-text-color, #000);
      }

      .quick-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
        margin-bottom: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid var(--divider-color, #e0e0e0);
      }

      .quick-action-button {
        padding: 6px 12px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 16px;
        background: var(--card-background-color, #fff);
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
        white-space: nowrap;
      }

      .quick-action-button:hover {
        background: var(--primary-color, #03a9f4);
        color: white;
        border-color: var(--primary-color, #03a9f4);
      }

      .input-container {
        display: flex;
        gap: 8px;
        margin-top: auto;
      }

      .input-field {
        flex: 1;
        padding: 10px 14px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 20px;
        font-size: 14px;
        outline: none;
      }

      .input-field:focus {
        border-color: var(--primary-color, #03a9f4);
      }

      .send-button {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: var(--primary-color, #03a9f4);
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      .send-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .empty-state {
        text-align: center;
        color: var(--secondary-text-color, #888);
        padding: 40px 20px;
        flex: 1;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    `;
  }

  constructor() {
    super();
    this._messages = [];
    this._isLoading = false;
    this._inputValue = "";
  }

  setConfig(config) {
    this.config = config;
  }

  getCardSize() {
    return 6; // Approximate card height in grid units
  }

  render() {
    return html`
      <div class="card">
        <div class="header">
          <ha-icon icon="mdi:robot"></ha-icon>
          <h2>${this.config?.title || "AI Assistant"}</h2>
        </div>

        ${this.config?.show_quick_actions !== false
          ? html`
              <div class="quick-actions">
                <button
                  class="quick-action-button"
                  @click=${() =>
                    this._sendQuickAction("Create an automation")}
                >
                  Create Automation
                </button>
                <button
                  class="quick-action-button"
                  @click=${() => this._sendQuickAction("Create a scene")}
                >
                  Create Scene
                </button>
                <button
                  class="quick-action-button"
                  @click=${() => this._sendQuickAction("Show my devices")}
                >
                  Show Devices
                </button>
              </div>
            `
          : ""}

        <div class="messages-container">
          ${this._messages.length === 0
            ? html`
                <div class="empty-state">
                  <div>
                    <p>Hi! I can help you control your smart home.</p>
                    <p style="font-size: 12px; margin-top: 8px;">
                      Try: "Turn on living room lights" or "Create an automation
                      to turn on lights at sunset"
                    </p>
                  </div>
                </div>
              `
            : this._messages.map(
                (msg) => html`
                  <div class="message ${msg.role}">${msg.content}</div>
                `
              )}
          ${this._isLoading
            ? html`<div class="message assistant">Thinking...</div>`
            : ""}
        </div>

        <div class="input-container">
          <input
            class="input-field"
            type="text"
            placeholder="Ask me anything..."
            .value=${this._inputValue}
            @input=${(e) => (this._inputValue = e.target.value)}
            @keypress=${this._handleKeyPress}
          />
          <button
            class="send-button"
            @click=${this._sendMessage}
            ?disabled=${this._isLoading || !this._inputValue.trim()}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
            </svg>
          </button>
        </div>
      </div>
    `;
  }

  _handleKeyPress(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      this._sendMessage();
    }
  }

  _sendQuickAction(action) {
    this._inputValue = action;
    this._sendMessage();
  }

  async _sendMessage() {
    if (!this._inputValue.trim() || this._isLoading) return;

    const userMessage = this._inputValue.trim();
    this._inputValue = "";
    this._messages = [...this._messages, { role: "user", content: userMessage }];
    this._isLoading = true;

    // Scroll to bottom
    this.updateComplete.then(() => {
      const container = this.shadowRoot.querySelector(".messages-container");
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    });

    try {
      const response = await this.hass.callService("ai_agent_ha", "query", {
        prompt: userMessage,
      });

      if (response && response.response) {
        this._messages = [
          ...this._messages,
          { role: "assistant", content: response.response },
        ];
      } else if (response && response.error) {
        this._messages = [
          ...this._messages,
          {
            role: "assistant",
            content: `Error: ${response.error}`,
          },
        ];
      }
    } catch (error) {
      this._messages = [
        ...this._messages,
        {
          role: "assistant",
          content: `Error: ${error.message || "Failed to get response"}`,
        },
      ];
    } finally {
      this._isLoading = false;
      // Scroll to bottom after response
      this.updateComplete.then(() => {
        const container = this.shadowRoot.querySelector(".messages-container");
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
  }
}

customElements.define("ai-agent-ha-card", AiAgentHaCard);

// Register as Lovelace card
window.customCards = window.customCards || [];
window.customCards.push({
  type: "ai-agent-ha-card",
  name: "AI Agent HA Card",
  description: "AI Assistant card for creating automations, scenes, and controlling your smart home",
});
