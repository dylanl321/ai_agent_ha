// Floating Action Button for AI Agent HA - Accessible from any page
import {
  LitElement,
  html,
  css,
} from "https://unpkg.com/lit-element@2.4.0/lit-element.js?module";

class AiAgentHaFab extends LitElement {
  static get properties() {
    return {
      hass: { type: Object },
      _isOpen: { type: Boolean },
      _messages: { type: Array },
      _isLoading: { type: Boolean },
      _inputValue: { type: String },
    };
  }

  static get styles() {
    return css`
      :host {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
      }

      .fab-button {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: var(--primary-color, #03a9f4);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.3s ease;
        position: relative;
      }

      .fab-button:hover {
        transform: scale(1.1);
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
      }

      .fab-button:active {
        transform: scale(0.95);
      }

      .chat-window {
        position: absolute;
        bottom: 70px;
        right: 0;
        width: 380px;
        max-width: calc(100vw - 40px);
        height: 500px;
        max-height: calc(100vh - 100px);
        background: var(--card-background-color, #fff);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        overflow: hidden;
      }

      .chat-header {
        padding: 16px;
        background: var(--primary-color, #03a9f4);
        color: white;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-weight: 500;
      }

      .close-button {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 4px;
        display: flex;
        align-items: center;
      }

      .messages-container {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }

      .message {
        padding: 10px 14px;
        border-radius: 12px;
        max-width: 80%;
        word-wrap: break-word;
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

      .input-container {
        padding: 12px;
        border-top: 1px solid var(--divider-color, #e0e0e0);
        display: flex;
        gap: 8px;
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
      }

      .send-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }

      .quick-actions {
        padding: 12px;
        border-top: 1px solid var(--divider-color, #e0e0e0);
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }

      .quick-action-button {
        padding: 6px 12px;
        border: 1px solid var(--divider-color, #e0e0e0);
        border-radius: 16px;
        background: var(--card-background-color, #fff);
        cursor: pointer;
        font-size: 12px;
        transition: all 0.2s;
      }

      .quick-action-button:hover {
        background: var(--primary-color, #03a9f4);
        color: white;
        border-color: var(--primary-color, #03a9f4);
      }

      @media (max-width: 600px) {
        .chat-window {
          width: calc(100vw - 20px);
          right: -10px;
        }
      }
    `;
  }

  constructor() {
    super();
    this._isOpen = false;
    this._messages = [];
    this._isLoading = false;
    this._inputValue = "";
  }

  render() {
    return html`
      ${this._isOpen ? this._renderChatWindow() : ""}
      <button class="fab-button" @click=${this._toggleChat}>
        <svg
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          ${this._isOpen
            ? html`<path d="M18 6L6 18M6 6l12 12" />`
            : html`<path
                d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
              />`}
        </svg>
      </button>
    `;
  }

  _renderChatWindow() {
    return html`
      <div class="chat-window">
        <div class="chat-header">
          <span>AI Assistant</span>
          <button class="close-button" @click=${this._toggleChat}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
            </svg>
          </button>
        </div>
        <div class="messages-container">
          ${this._messages.length === 0
            ? html`
                <div class="message assistant">
                  Hi! I can help you control your smart home, create automations,
                  and manage dashboards. What would you like to do?
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
        <div class="quick-actions">
          <button
            class="quick-action-button"
            @click=${() => this._sendQuickAction("Create an automation")}
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
            @click=${() => this._sendQuickAction("Show me my lights")}
          >
            Show Lights
          </button>
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

  _toggleChat() {
    this._isOpen = !this._isOpen;
    if (this._isOpen && this._messages.length === 0) {
      // Auto-scroll to bottom when opening
      this.updateComplete.then(() => {
        const container = this.shadowRoot.querySelector(".messages-container");
        if (container) {
          container.scrollTop = container.scrollHeight;
        }
      });
    }
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

customElements.define("ai-agent-ha-fab", AiAgentHaFab);
