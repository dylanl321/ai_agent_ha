# Library Integration in HACS Packages

This document outlines best practices and methods for incorporating external libraries in HACS (Home Assistant Community Store) custom components.

## Overview

HACS packages can include both **Python** (backend) and **JavaScript** (frontend) libraries. The approach differs for each:

## Python Libraries (Backend)

### Method 1: requirements.txt (Recommended)

**Current Implementation:**
- ✅ Already using this method for `boto3`, `aiohttp`, `voluptuous`
- ✅ Home Assistant automatically installs dependencies from `requirements.txt`

**How it works:**
1. Add dependencies to `requirements.txt`:
   ```txt
   aiohttp>=3.8.0
   voluptuous>=0.13.1
   boto3>=1.28.0
   ```

2. Home Assistant installs them via pip during integration setup
3. Import in your Python code:
   ```python
   import boto3
   from botocore.exceptions import ClientError
   ```

**Best Practices:**
- Pin versions with `>=` for minimum versions
- Test with different versions
- Keep dependencies minimal
- Document in README

### Method 2: manifest.json (Alternative)

Some integrations declare dependencies in `manifest.json`:
```json
{
  "dependencies": ["boto3>=1.28.0"]
}
```

However, `requirements.txt` is more standard and widely used.

## JavaScript Libraries (Frontend)

### Current Challenge

Your panel uses CDN imports which can fail:
```javascript
import { marked } from "https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js";
```

**Issues:**
- ❌ CDN failures prevent panel loading
- ❌ Network dependency
- ❌ CORS issues in some environments
- ❌ No offline support

### Method 1: Bundle Libraries Locally (Recommended)

**Best Practice:** Include minified/bundled libraries in your `frontend/` directory.

#### Option A: Manual Download & Include

1. Download the library (ESM or UMD version)
2. Place in `custom_components/ai_agent_ha/frontend/libs/`
3. Import locally:
   ```javascript
   import { marked } from "/frontend/ai_agent_ha/libs/marked.esm.js";
   ```

**Pros:**
- ✅ No network dependency
- ✅ Works offline
- ✅ Reliable loading
- ✅ Version control

**Cons:**
- ❌ Increases package size
- ❌ Manual updates required

#### Option B: Build Process with npm/webpack

1. Create `package.json`:
   ```json
   {
     "name": "ai-agent-ha-frontend",
     "version": "1.0.0",
     "type": "module",
     "dependencies": {
       "marked": "^11.1.1",
       "dompurify": "^3.0.6"
     },
     "devDependencies": {
       "rollup": "^4.0.0",
       "@rollup/plugin-node-resolve": "^15.0.0"
     }
   }
   ```

2. Create `rollup.config.js`:
   ```javascript
   import resolve from '@rollup/plugin-node-resolve';

   export default {
     input: 'custom_components/ai_agent_ha/frontend/ai_agent_ha-panel.js',
     output: {
       file: 'custom_components/ai_agent_ha/frontend/ai_agent_ha-panel.bundle.js',
       format: 'es'
     },
     plugins: [resolve()],
     external: ['lit-element', 'lit-html'] // Keep these as CDN imports
   };
   ```

3. Build:
   ```bash
   npm install
   npm run build
   ```

4. Update panel registration to use bundled file:
   ```python
   "module_url": "/frontend/ai_agent_ha/ai_agent_ha-panel.bundle.js"
   ```

**Pros:**
- ✅ Automated bundling
- ✅ Tree shaking (smaller bundles)
- ✅ Easy dependency management
- ✅ Version control via package.json

**Cons:**
- ❌ Requires build step
- ❌ More complex setup
- ❌ Need to document build process

### Method 2: CDN with Fallback (Current Approach - Improved)

**Current Implementation:**
- ✅ Lazy loading (non-blocking)
- ✅ Fallback parser if CDN fails
- ✅ Works even if libraries don't load

**Improvements:**
1. Add multiple CDN sources:
   ```javascript
   const CDN_SOURCES = [
     "https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js",
     "https://unpkg.com/marked@11.1.1/lib/marked.esm.js",
     "/frontend/ai_agent_ha/libs/marked.esm.js" // Local fallback
   ];
   ```

2. Try each source sequentially
3. Cache successful loads
4. Always have a fallback implementation

### Method 3: Use Home Assistant Built-ins

**Check if HA provides the library:**
- Home Assistant frontend includes some libraries
- Check HA source code for available modules
- Import from HA's internal modules (if documented)

**Example:**
```javascript
// If HA provides markdown parsing
import { parseMarkdown } from "/frontend_latest/common/markdown.js";
```

**Note:** This is risky as HA internals can change.

## Recommended Approach for Your Project

### For Markdown Parsing

**Option 1: Bundle Locally (Best for Reliability)**
1. Download `marked.min.js` and `dompurify.min.js`
2. Place in `frontend/libs/`
3. Import locally:
   ```javascript
   import { marked } from "/frontend/ai_agent_ha/libs/marked.esm.js";
   import DOMPurify from "/frontend/ai_agent_ha/libs/purify.es.mjs";
   ```

**Option 2: Keep Current Fallback (Good for Now)**
- Current implementation works
- Fallback parser handles most cases
- Libraries load in background if available

### Implementation Steps for Bundling

1. **Create libs directory:**
   ```bash
   mkdir -p custom_components/ai_agent_ha/frontend/libs
   ```

2. **Download libraries:**
   ```bash
   # Download marked.js ESM version
   curl -o custom_components/ai_agent_ha/frontend/libs/marked.esm.js \
     https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js
   
   # Download DOMPurify ESM version
   curl -o custom_components/ai_agent_ha/frontend/libs/purify.es.mjs \
     https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.es.mjs
   ```

3. **Update imports:**
   ```javascript
   // Change from:
   import { marked } from "https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js";
   
   // To:
   import { marked } from "/frontend/ai_agent_ha/libs/marked.esm.js";
   ```

4. **Update static path registration** (if needed):
   ```python
   # Already registered, should work automatically
   StaticPathConfig(
       "/frontend/ai_agent_ha",
       hass.config.path("custom_components/ai_agent_ha/frontend"),
       False,
   )
   ```

## Build Tools Setup (Advanced)

### Using npm + Rollup

1. **Initialize npm:**
   ```bash
   npm init -y
   ```

2. **Install dependencies:**
   ```bash
   npm install --save marked dompurify
   npm install --save-dev rollup @rollup/plugin-node-resolve
   ```

3. **Create build script:**
   ```json
   {
     "scripts": {
       "build": "rollup -c",
       "build:watch": "rollup -c --watch"
     }
   }
   ```

4. **Add to .gitignore:**
   ```
   node_modules/
   package-lock.json
   *.bundle.js
   ```

5. **Document in README:**
   ```markdown
   ## Development
   
   To build the frontend:
   ```bash
   npm install
   npm run build
   ```
   ```

## HACS-Specific Considerations

### Package Size
- HACS has no strict size limit, but keep it reasonable
- Bundled libraries add ~50-200KB typically
- Consider tree-shaking for large libraries

### Version Control
- ✅ Commit bundled libraries to git
- ✅ Document library versions
- ✅ Update libraries periodically

### Distribution
- HACS downloads entire repository
- All files in `custom_components/` are included
- Users get everything they need

### Testing
- Test with and without internet
- Test with different HA versions
- Test CDN availability scenarios

## Comparison Table

| Method | Reliability | Setup Complexity | Package Size | Maintenance |
|--------|-------------|----------------|--------------|-------------|
| **CDN** | ⚠️ Medium | ✅ Easy | ✅ Small | ⚠️ Medium |
| **CDN + Fallback** | ✅ Good | ✅ Easy | ✅ Small | ✅ Easy |
| **Local Bundle** | ✅ Excellent | ⚠️ Medium | ⚠️ Larger | ⚠️ Medium |
| **Build Process** | ✅ Excellent | ❌ Complex | ✅ Optimized | ✅ Easy |

## Recommendations

### For Your Project (AI Agent HA)

**Short Term:**
- ✅ Keep current CDN + fallback approach
- ✅ Improve fallback parser quality
- ✅ Add multiple CDN sources

**Long Term:**
- 📦 Bundle critical libraries locally
- 🔧 Set up build process for development
- 📝 Document library versions
- 🧪 Test offline scenarios

### General Best Practices

1. **Python Libraries:** Always use `requirements.txt`
2. **JavaScript Libraries:**
   - Critical libraries: Bundle locally
   - Optional libraries: CDN with fallback
   - Large libraries: Use build process
3. **Documentation:** Always document dependencies
4. **Testing:** Test with and without network
5. **Updates:** Keep libraries updated for security

## Example: Complete Setup

### Directory Structure
```
custom_components/ai_agent_ha/
├── frontend/
│   ├── ai_agent_ha-panel.js
│   ├── libs/
│   │   ├── marked.esm.js
│   │   └── purify.es.mjs
│   └── ...
├── __init__.py
├── agent.py
└── ...
requirements.txt
package.json (optional)
rollup.config.js (optional)
```

### Updated Panel Code
```javascript
// Try local first, then CDN, then fallback
let marked = null;
let DOMPurify = null;

async function loadMarkdownLibraries() {
  const sources = {
    marked: [
      "/frontend/ai_agent_ha/libs/marked.esm.js",
      "https://cdn.jsdelivr.net/npm/marked@11.1.1/lib/marked.esm.js",
      "https://unpkg.com/marked@11.1.1/lib/marked.esm.js"
    ],
    dompurify: [
      "/frontend/ai_agent_ha/libs/purify.es.mjs",
      "https://cdn.jsdelivr.net/npm/dompurify@3.0.6/dist/purify.es.mjs"
    ]
  };
  
  // Try each source until one works
  for (const source of sources.marked) {
    try {
      const module = await import(source);
      marked = module.marked || module.default || module;
      break;
    } catch (e) {
      console.debug(`Failed to load marked from ${source}`);
    }
  }
  
  // Similar for DOMPurify...
}
```

## References

- [HACS Documentation](https://hacs.xyz/docs/)
- [Home Assistant Custom Components](https://developers.home-assistant.io/docs/creating_integration_manifest/)
- [ES Modules in Home Assistant](https://developers.home-assistant.io/docs/frontend/custom-ui/)
- [npm Documentation](https://docs.npmjs.com/)
- [Rollup Documentation](https://rollupjs.org/)

## Conclusion

For HACS packages:
- **Python libraries:** Use `requirements.txt` ✅
- **JavaScript libraries:** Bundle locally for reliability, CDN with fallback for flexibility
- **Always have a fallback** for critical functionality
- **Document everything** for maintainability

Your current approach (CDN + fallback) is good, but bundling locally would be more reliable for production use.
