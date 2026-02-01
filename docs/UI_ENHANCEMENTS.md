# UI Enhancements - Global Access to AI Agent HA

This document explains how to use the AI Agent HA chat system from anywhere in Home Assistant, not just the dedicated panel.

## Available Components

### 1. Floating Action Button (FAB)
A floating chat button that appears on all pages, providing quick access to the AI assistant.

### 2. Lovelace Card
A card component that can be added to any dashboard for inline chat functionality.

## Setup Instructions

### Option 1: Floating Action Button (Recommended)

The FAB provides a floating chat button accessible from any page. To enable it:

1. **Add as a Lovelace Resource:**
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **Add Resource** (bottom right)
   - Enter URL: `/local/ai_agent_ha/frontend/ai_agent_ha-fab.js`
   - Set Resource Type: **JavaScript Module**
   - Click **Create**

2. **Add to a Dashboard View:**
   Add this YAML to any dashboard view where you want the FAB:

   ```yaml
   type: custom:ai-agent-ha-fab
   ```

   Or add it as a card in your dashboard YAML:

   ```yaml
   views:
     - title: Home
       cards:
         - type: custom:ai-agent-ha-fab
   ```

3. **Automatic Global Injection (Easiest)**
   For the FAB to appear automatically on ALL pages:
   
   - Add **TWO** resources:
     1. `/local/ai_agent_ha/frontend/ai_agent_ha-fab.js` (type: JavaScript Module)
     2. `/local/ai_agent_ha/frontend/ai_agent_ha-global.js` (type: JavaScript Module)
   
   The global script will automatically inject the FAB on every page.

### Option 2: Lovelace Card

Add the AI Assistant as a card to any dashboard:

1. **Add as a Lovelace Resource:**
   - Go to **Settings** → **Dashboards** → **Resources**
   - Click **Add Resource**
   - Enter URL: `/local/ai_agent_ha/frontend/ai_agent_ha-card.js`
   - Set Resource Type: **JavaScript Module**
   - Click **Create**

2. **Add Card to Dashboard:**
   - Edit your dashboard
   - Click **Add Card**
   - Search for **AI Agent HA Card** or use **Manual** card
   - Add this YAML:

   ```yaml
   type: custom:ai-agent-ha-card
   title: AI Assistant
   show_quick_actions: true
   ```

## Quick Actions

Both components include quick action buttons for common tasks:

- **Create Automation** - Opens chat with "Create an automation" prompt
- **Create Scene** - Opens chat with "Create a scene" prompt  
- **Show Devices/Lights** - Opens chat to view your devices

## Features

### Floating Action Button
- ✅ Always accessible from any page
- ✅ Compact floating button
- ✅ Expandable chat window
- ✅ Quick action buttons
- ✅ Mobile responsive

### Lovelace Card
- ✅ Integrates seamlessly into dashboards
- ✅ Customizable title
- ✅ Optional quick actions
- ✅ Full chat functionality
- ✅ Responsive design

## Usage Examples

### Create Automation from Anywhere

1. Click the FAB button or open the card
2. Click **Create Automation** or type: "Create an automation to turn on lights at sunset"
3. The AI will guide you through the process

### Create Scene Quickly

1. Open the chat (FAB or card)
2. Click **Create Scene** or type: "Create a scene called 'Movie Night' that dims the lights"
3. Follow the AI's prompts

### Control Devices

1. Open the chat
2. Type natural language commands like:
   - "Turn on living room lights"
   - "Set temperature to 72 degrees"
   - "Show me all my sensors"

## Configuration Options

### FAB Configuration
The FAB currently uses default styling. Future versions may support:
- Custom positioning
- Custom colors
- Auto-hide options

### Card Configuration
```yaml
type: custom:ai-agent-ha-card
title: My AI Assistant        # Custom title
show_quick_actions: true       # Show/hide quick action buttons
```

## Troubleshooting

### FAB Not Appearing
- Ensure the resource is added correctly
- Check browser console for errors
- Verify the file path is correct: `/local/ai_agent_ha/frontend/ai_agent_ha-fab.js`

### Card Not Loading
- Ensure the resource is added
- Check that the card type is exactly: `custom:ai-agent-ha-card`
- Clear browser cache and reload

### Service Errors
- Ensure AI Agent HA integration is configured
- Check that at least one AI provider is set up
- Verify the `ai_agent_ha.query` service is available

## Advanced: Custom Integration

You can also call the AI Agent HA service directly from automations, scripts, or other components:

```yaml
service: ai_agent_ha.query
data:
  prompt: "Turn on all lights"
```

## Future Enhancements

Planned features:
- Context-aware quick actions based on current page
- Voice input support
- Integration with entity cards for quick actions
- Customizable FAB appearance
- Multiple chat instances
- Chat history persistence
