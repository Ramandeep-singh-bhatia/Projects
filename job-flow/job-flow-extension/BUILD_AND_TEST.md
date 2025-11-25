# JobFlow Extension - Build and Testing Guide

Complete guide for building, testing, and debugging the JobFlow Chrome extension.

## Table of Contents

1. [Development Setup](#development-setup)
2. [Building the Extension](#building-the-extension)
3. [Testing Guide](#testing-guide)
4. [Platform-Specific Testing](#platform-specific-testing)
5. [Debugging](#debugging)
6. [Common Issues](#common-issues)
7. [Development Workflow](#development-workflow)

---

## Development Setup

### Prerequisites

- Node.js 18+ and npm 8+
- Chrome or Chromium browser (version 88+)
- Backend running at `http://localhost:8000`
- Basic knowledge of Chrome DevTools

### Initial Setup

```bash
cd job-flow-extension

# Install dependencies
npm install

# Verify installation
npm list --depth=0
```

**Expected Dependencies:**
```
├── react@18.2.0
├── react-dom@18.2.0
├── typescript@5.0.0
├── webpack@5.88.0
├── webpack-cli@5.1.4
├── @types/chrome@0.0.246
└── ... (see package.json for complete list)
```

### Project Structure

```
job-flow-extension/
├── src/
│   ├── background/           # Service worker
│   │   └── service-worker.ts
│   ├── content/              # Content scripts
│   │   ├── content-script.ts
│   │   ├── form-detector.ts
│   │   ├── field-mapper.ts
│   │   └── platform-handlers/
│   │       ├── base-handler.ts
│   │       ├── linkedin-handler.ts
│   │       ├── workday-handler.ts
│   │       ├── greenhouse-handler.ts
│   │       ├── lever-handler.ts
│   │       └── index.ts
│   ├── popup/                # Popup UI
│   │   ├── Popup.tsx
│   │   └── popup.html
│   ├── options/              # Options page
│   │   ├── Options.tsx
│   │   └── options.html
│   └── shared/               # Shared utilities
│       ├── api/
│       │   └── backend-client.ts
│       ├── types/
│       │   └── index.ts
│       └── utils/
│           ├── storage.ts
│           └── logger.ts
├── public/
│   ├── manifest.json
│   └── icons/
├── dist/                     # Build output (generated)
├── webpack.config.js
├── tsconfig.json
└── package.json
```

---

## Building the Extension

### Development Build

Development build with source maps and watch mode:

```bash
# One-time build
npm run dev

# Watch mode (rebuilds on file changes)
npm run watch
```

**Output:** `dist/` folder with:
- `content-script.js` - Content script bundle
- `service-worker.js` - Background service worker
- `popup.js` & `popup.html` - Popup UI
- `options.js` & `options.html` - Options page
- `manifest.json` - Extension manifest
- Source maps (`.map` files)

### Production Build

Optimized production build:

```bash
npm run build
```

**Optimizations:**
- Minified JavaScript
- Tree-shaking for smaller bundles
- No source maps (optional: enable in webpack config)
- Optimized React production build

**Bundle Sizes (approximate):**
- `content-script.js`: ~150KB (minified)
- `service-worker.js`: ~50KB (minified)
- `popup.js`: ~200KB (includes React)
- `options.js`: ~220KB (includes React)

### Build Configuration

Edit `webpack.config.js` to customize:

```javascript
// Enable source maps in production
devtool: 'source-map',

// Adjust bundle splitting
optimization: {
  splitChunks: {
    chunks: 'all',
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendor',
        priority: 10
      }
    }
  }
}

// Add additional plugins
plugins: [
  new webpack.DefinePlugin({
    'process.env.API_URL': JSON.stringify('http://localhost:8000')
  })
]
```

### Loading in Chrome

**Step-by-step:**

1. Build the extension:
   ```bash
   npm run build
   ```

2. Open Chrome and navigate to:
   ```
   chrome://extensions/
   ```

3. Enable "Developer mode" (toggle in top-right corner)

4. Click "Load unpacked"

5. Navigate to and select:
   ```
   /path/to/job-flow-extension/dist
   ```

6. Extension should appear with JobFlow icon

7. Pin extension for easy access:
   - Click puzzle piece icon in Chrome toolbar
   - Click pin icon next to JobFlow

**Reloading After Changes:**

```bash
# 1. Make code changes
# 2. Rebuild
npm run build

# 3. In chrome://extensions/, click refresh icon on JobFlow card
# OR press Ctrl+R on extensions page
```

**Hot Reload (Advanced):**

For true hot reload during development, use watch mode + auto-reload extension:

```bash
# Terminal 1: Watch mode
npm run watch

# Terminal 2: Extension reloader (optional npm package)
npm install -g chrome-extension-auto-reload
chrome-extension-auto-reload dist
```

---

## Testing Guide

### Manual Testing Checklist

#### Backend Connection Test

1. Start backend:
   ```bash
   cd job-flow-backend
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

2. Open extension popup

3. Check connection status:
   - Green checkmark = Connected
   - Red X = Not connected

4. If not connected:
   - Click Settings → Backend URL
   - Enter `http://localhost:8000`
   - Click "Test Connection"

#### Profile Test

1. Open extension options (right-click icon → Options)

2. Fill in profile information:
   - Required: First name, last name, email, phone
   - Optional: LinkedIn, GitHub, website

3. Click "Save Profile"

4. Verify in backend:
   ```bash
   curl http://localhost:8000/api/profile
   ```

5. Should return your profile data

#### Question Matching Test

1. Add test question via backend:
   ```bash
   curl -X POST http://localhost:8000/api/questions \
     -H "Content-Type: application/json" \
     -d '{
       "question_text": "What is your email address?",
       "answer_text": "test@example.com",
       "category": "contact"
     }'
   ```

2. Test matching:
   ```bash
   curl -X POST http://localhost:8000/api/questions/match \
     -H "Content-Type: application/json" \
     -d '{"question_text": "Email?"}'
   ```

3. Should return match with confidence score

#### Form Detection Test

**Create Test HTML Page:**

```html
<!-- test-form.html -->
<!DOCTYPE html>
<html>
<head>
  <title>JobFlow Test Form</title>
</head>
<body>
  <h1>Test Application Form</h1>

  <form id="test-form">
    <label for="first-name">First Name</label>
    <input type="text" id="first-name" name="first_name">

    <label for="last-name">Last Name</label>
    <input type="text" id="last-name" name="last_name">

    <label for="email">Email Address</label>
    <input type="email" id="email" name="email">

    <label for="phone">Phone Number</label>
    <input type="tel" id="phone" name="phone">

    <label for="linkedin">LinkedIn Profile URL</label>
    <input type="url" id="linkedin" name="linkedin_url">

    <label for="experience">Years of Experience</label>
    <select id="experience" name="years_experience">
      <option value="">Select...</option>
      <option value="0-2">0-2 years</option>
      <option value="3-5">3-5 years</option>
      <option value="6-10">6-10 years</option>
      <option value="10+">10+ years</option>
    </select>

    <label for="work-auth">Work Authorization</label>
    <select id="work-auth" name="work_authorization">
      <option value="">Select...</option>
      <option value="citizen">US Citizen</option>
      <option value="green_card">Green Card Holder</option>
      <option value="visa">Work Visa</option>
      <option value="need_sponsorship">Need Sponsorship</option>
    </select>

    <label for="remote">Remote Work Preference</label>
    <div>
      <input type="radio" id="remote-only" name="remote_pref" value="remote_only">
      <label for="remote-only">Remote Only</label>

      <input type="radio" id="remote-flexible" name="remote_pref" value="flexible">
      <label for="remote-flexible">Flexible</label>

      <input type="radio" id="office-only" name="remote_pref" value="office">
      <label for="office-only">Office Only</label>
    </div>

    <label for="relocate">Willing to Relocate?</label>
    <input type="checkbox" id="relocate" name="willing_to_relocate">

    <label for="cover-letter">Cover Letter</label>
    <textarea id="cover-letter" name="cover_letter" rows="5"></textarea>

    <button type="submit">Submit Application</button>
  </form>

  <script>
    document.getElementById('test-form').addEventListener('submit', (e) => {
      e.preventDefault();
      alert('Form submitted! Check field values.');
    });
  </script>
</body>
</html>
```

**Test Steps:**

1. Save test-form.html and open in Chrome

2. Press **Ctrl+Shift+F**

3. Verify notification appears:
   ```
   ✓ JobFlow detected 11 fields
   ```

4. Check that fields are filled correctly

5. Open DevTools Console to see logs:
   ```
   [JobFlow] Detected form with 11 fields
   [JobFlow] Filling field: First Name
   [JobFlow] Filling field: Last Name
   ...
   ```

### Automated Testing

#### Unit Tests (Future Enhancement)

Create test files in `src/__tests__/`:

```typescript
// src/__tests__/form-detector.test.ts
import { FormDetector } from '../content/form-detector';

describe('FormDetector', () => {
  let detector: FormDetector;

  beforeEach(() => {
    detector = new FormDetector();
  });

  test('detects form with <form> tag', () => {
    document.body.innerHTML = `
      <form>
        <input type="text" name="name">
        <input type="email" name="email">
      </form>
    `;

    const forms = detector.detectForms();
    expect(forms).toHaveLength(1);
  });

  test('detects form-like container without <form> tag', () => {
    document.body.innerHTML = `
      <div id="application">
        <input type="text" name="field1">
        <input type="text" name="field2">
        <input type="text" name="field3">
        <input type="text" name="field4">
        <input type="text" name="field5">
      </div>
    `;

    const forms = detector.detectForms();
    expect(forms.length).toBeGreaterThan(0);
  });

  test('extracts field labels correctly', () => {
    document.body.innerHTML = `
      <form>
        <label for="email">Email Address</label>
        <input type="email" id="email" name="email">
      </form>
    `;

    const forms = detector.detectForms();
    const fields = detector.extractFields(forms[0]);

    expect(fields[0].label).toBe('Email Address');
  });
});
```

**Run Tests:**

```bash
# Install testing dependencies
npm install --save-dev jest @types/jest ts-jest @testing-library/react @testing-library/jest-dom

# Add to package.json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage"
  }
}

# Run tests
npm test
```

#### Integration Tests

Test complete workflows:

```typescript
// src/__tests__/integration/application-flow.test.ts
describe('Complete Application Flow', () => {
  test('fills LinkedIn Easy Apply form', async () => {
    // 1. Mock backend responses
    // 2. Load test page with LinkedIn-like form
    // 3. Trigger auto-fill
    // 4. Verify all fields are filled
    // 5. Check backend API calls
  });
});
```

---

## Platform-Specific Testing

### LinkedIn Easy Apply

**Finding Test Jobs:**

1. Go to LinkedIn Jobs
2. Search for "software engineer"
3. Filter by "Easy Apply"
4. Open any job with Easy Apply button

**Test Checklist:**

- [ ] Click "Easy Apply" button
- [ ] Modal appears with application form
- [ ] Press Ctrl+Shift+F
- [ ] Notification shows "✓ JobFlow detected LinkedIn Easy Apply"
- [ ] Contact info fields are filled
- [ ] Phone number formatted correctly
- [ ] Resume section shows status
- [ ] Click "Continue" to next step
- [ ] Repeat auto-fill on each step
- [ ] All steps complete successfully
- [ ] "Review" page shows all data correctly

**Common Fields:**

| Field | Expected Value | Source |
|-------|----------------|--------|
| Phone | +1-555-123-4567 | user_profiles.phone |
| City | San Francisco | user_profiles.city |
| LinkedIn Profile | https://linkedin.com/in/username | user_profiles.linkedin_url |
| Work Authorization | Yes / No | user_profiles.work_authorization |
| Sponsorship | Yes / No | user_profiles.requires_sponsorship |
| Years Experience | 5 | user_profiles.years_of_experience |

**Debug Commands:**

```javascript
// In DevTools Console on LinkedIn page:

// Check if handler detected
console.log('Platform:', window.location.hostname);

// Check detected fields
chrome.storage.local.get(['detected_fields'], console.log);

// Force re-detection
location.reload();
```

### Workday

**Finding Test Jobs:**

Many companies use Workday. Search for jobs at:
- Netflix: `netflix.wd1.myworkdayjobs.com`
- Amazon: `amazon.jobs` (uses Workday)
- Walmart: `careers.walmart.com`
- Tesla: `tesla.wd5.myworkdayjobs.com`

**Test Checklist:**

- [ ] Navigate to Workday application page
- [ ] Account creation may be required (first time)
- [ ] Press Ctrl+Shift+F on first step
- [ ] Notification shows "✓ JobFlow detected Workday"
- [ ] Fields filled with data-automation-id selectors
- [ ] Resume upload detected (if present)
- [ ] Click "Next" button
- [ ] Repeat on subsequent steps
- [ ] Complete all steps successfully

**Workday-Specific Fields:**

| Field | data-automation-id | Expected Value |
|-------|-------------------|----------------|
| First Name | legalNameSection_firstName | John |
| Last Name | legalNameSection_lastName | Doe |
| Email | email | john.doe@email.com |
| Phone | phone | +1-555-123-4567 |
| Address | addressSection_city | San Francisco |

**Debug Tips:**

```javascript
// Find all data-automation-id attributes
document.querySelectorAll('[data-automation-id]').forEach(el => {
  console.log(el.getAttribute('data-automation-id'), el.tagName);
});

// Check if on review page
const reviewPage = document.querySelector('[data-automation-id*="review"]');
console.log('Review page:', !!reviewPage);
```

### Greenhouse

**Finding Test Jobs:**

Search GitHub jobs or companies using Greenhouse:
- Shopify: `shopify.greenhouse.io`
- Airbnb: `airbnb.greenhouse.io`
- Stripe: `stripe.com/jobs` (uses Greenhouse)

**Test Checklist:**

- [ ] Navigate to Greenhouse application page
- [ ] Form loads (single page usually)
- [ ] Press Ctrl+Shift+F
- [ ] Notification shows "✓ JobFlow detected Greenhouse"
- [ ] All fields filled
- [ ] Resume file upload detected
- [ ] Submit button visible
- [ ] Review before submitting

**Greenhouse Structure:**

```html
<!-- Typical Greenhouse HTML -->
<div class="application-form">
  <div class="field">
    <label>First Name</label>
    <input type="text" name="first_name">
  </div>

  <div class="field">
    <label>Email</label>
    <input type="email" name="email">
  </div>

  <!-- Resume upload -->
  <div class="field">
    <label>Resume/CV</label>
    <input type="file" name="resume">
  </div>
</div>
```

### Lever

**Finding Test Jobs:**

Companies using Lever:
- Figma: `jobs.lever.co/figma`
- Netflix: Uses both Workday and Lever
- Many startups

**Test Checklist:**

- [ ] Navigate to Lever application page
- [ ] Form appears (usually single page)
- [ ] Press Ctrl+Shift+F
- [ ] Notification shows "✓ JobFlow detected Lever"
- [ ] All fields filled correctly
- [ ] Cover letter textarea filled
- [ ] File upload detected

**Lever Structure:**

```html
<!-- Typical Lever HTML -->
<form class="application-form">
  <div class="application-question">
    <div class="application-label">Full Name</div>
    <input type="text" name="name">
  </div>

  <div class="application-question">
    <div class="application-label">Email</div>
    <input type="email" name="email">
  </div>
</form>
```

---

## Debugging

### Chrome DevTools Setup

**Open DevTools for Different Contexts:**

1. **Popup UI:**
   - Right-click extension icon → "Inspect popup"
   - DevTools opens for popup.html

2. **Options Page:**
   - Right-click extension icon → "Options"
   - Press F12 on options page

3. **Content Script:**
   - Open job application page
   - Press F12 for normal DevTools
   - Content script logs appear here

4. **Background Service Worker:**
   - Go to `chrome://extensions/`
   - Find JobFlow extension
   - Click "service worker" link
   - DevTools opens for background script

### Logging Levels

JobFlow uses structured logging:

```typescript
// In any script, import logger
import { logger } from '../shared/utils/logger';

// Log levels
logger.debug('Detailed debug info');
logger.info('General information');
logger.warn('Warning message');
logger.error('Error occurred', error);
```

**Enable Verbose Logging:**

```javascript
// In DevTools Console:
localStorage.setItem('jobflow_debug', 'true');
location.reload();

// Disable:
localStorage.removeItem('jobflow_debug');
location.reload();
```

**Log Output Examples:**

```
[JobFlow][INFO] Content script initialized
[JobFlow][INFO] Detected 15 form fields
[JobFlow][DEBUG] Field: email, Type: email, Selector: input#email
[JobFlow][INFO] Filling field: email with value: john@example.com
[JobFlow][WARN] Could not find answer for question: "Custom question here"
[JobFlow][ERROR] Failed to fill field: phone, Error: Element not visible
```

### Common Debugging Scenarios

#### Fields Not Detecting

**Debug Steps:**

1. Open DevTools Console

2. Check if content script loaded:
   ```javascript
   console.log('JobFlow loaded:', typeof window.jobFlowContentScript);
   ```

3. If undefined, check manifest.json matches field permissions:
   ```json
   {
     "content_scripts": [{
       "matches": ["*://*.linkedin.com/*", ...],
       "js": ["content-script.js"]
     }]
   }
   ```

4. Manually trigger detection:
   ```javascript
   // Force re-detection
   window.postMessage({ type: 'JOBFLOW_DETECT' }, '*');
   ```

5. Check detected forms:
   ```javascript
   chrome.storage.local.get(['detected_fields'], (result) => {
     console.table(result.detected_fields);
   });
   ```

#### Fields Filling Incorrectly

**Debug Steps:**

1. Check field mapping:
   ```javascript
   // See what value is being used
   chrome.storage.local.get(['user_profile'], (result) => {
     console.log('Profile:', result.user_profile);
   });
   ```

2. Check question matching:
   ```bash
   # Test backend matching
   curl -X POST http://localhost:8000/api/questions/match \
     -H "Content-Type: application/json" \
     -d '{"question_text": "The exact field label here"}'
   ```

3. Add custom mapping:
   ```bash
   curl -X POST http://localhost:8000/api/questions \
     -H "Content-Type: application/json" \
     -d '{
       "question_text": "Exact field label",
       "answer_text": "Your answer",
       "confidence_score": 100
     }'
   ```

#### Platform Handler Not Activating

**Debug Steps:**

1. Check URL matching:
   ```javascript
   // In Console:
   console.log('URL:', window.location.href);
   console.log('Hostname:', window.location.hostname);
   ```

2. Check handler detection:
   ```javascript
   import { getPlatformHandler, getCurrentPlatformName } from './platform-handlers';

   const handler = getPlatformHandler();
   console.log('Handler:', handler ? handler.constructor.name : 'None');
   console.log('Platform:', getCurrentPlatformName());
   ```

3. Manually test handler:
   ```javascript
   // For LinkedIn:
   const modal = document.querySelector('.jobs-easy-apply-modal');
   console.log('LinkedIn modal found:', !!modal);
   ```

### Network Debugging

**Monitor Backend API Calls:**

1. Open DevTools → Network tab

2. Filter by XHR/Fetch

3. Look for calls to `localhost:8000`

4. Check request/response:
   ```
   POST http://localhost:8000/api/questions/match
   Request: {"question_text": "Email?"}
   Response: {"matched": true, "answer_text": "john@example.com", "confidence": 95}
   ```

5. Common issues:
   - CORS errors: Backend not running or misconfigured
   - 404 errors: Wrong backend URL in settings
   - 500 errors: Backend error, check server logs

---

## Common Issues

### Issue: Extension not loading

**Symptoms:**
- Extension not visible in chrome://extensions/
- No icon in toolbar

**Solutions:**

1. Check manifest.json is valid:
   ```bash
   # Validate JSON syntax
   cat dist/manifest.json | json_pp
   ```

2. Check webpack build completed:
   ```bash
   ls -la dist/
   # Should see: manifest.json, content-script.js, etc.
   ```

3. Reload extension:
   - chrome://extensions/ → Click refresh icon

4. Check for errors:
   - chrome://extensions/ → Click "Errors" button

### Issue: Backend connection failed

**Symptoms:**
- Red X in popup status
- "Failed to connect" errors

**Solutions:**

1. Verify backend is running:
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status": "healthy"}
   ```

2. Check backend URL in extension settings

3. Check CORS configuration:
   ```python
   # In job-flow-backend/app/main.py
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"],  # For development
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```

4. Try different port:
   ```bash
   uvicorn app.main:app --reload --port 8001
   # Update extension settings to http://localhost:8001
   ```

### Issue: TypeScript errors during build

**Symptoms:**
- Build fails with TS errors
- Type checking errors

**Solutions:**

1. Check tsconfig.json is correct

2. Install missing type definitions:
   ```bash
   npm install --save-dev @types/chrome @types/react @types/react-dom
   ```

3. Skip type checking (temporary):
   ```json
   // In webpack.config.js
   module: {
     rules: [{
       test: /\.tsx?$/,
       use: {
         loader: 'ts-loader',
         options: {
           transpileOnly: true  // Skip type checking
         }
       }
     }]
   }
   ```

4. Run type check separately:
   ```bash
   npx tsc --noEmit
   ```

### Issue: Form not auto-filling

**Symptoms:**
- Notification appears but fields don't fill
- Some fields fill, others don't

**Solutions:**

1. Check if fields are visible:
   ```javascript
   // Some forms hide fields initially
   const field = document.querySelector('#email');
   console.log('Visible:', field.offsetParent !== null);
   ```

2. Check field is not disabled:
   ```javascript
   console.log('Disabled:', field.disabled);
   console.log('Readonly:', field.readOnly);
   ```

3. Try manual field fill:
   ```javascript
   const field = document.querySelector('#email');
   field.value = 'test@example.com';
   field.dispatchEvent(new Event('input', { bubbles: true }));
   field.dispatchEvent(new Event('change', { bubbles: true }));
   ```

4. Increase delays in base-handler.ts:
   ```typescript
   // Increase from 50-100ms to 100-200ms
   await this.humanDelay(100, 200);
   ```

---

## Development Workflow

### Daily Development Process

**1. Start Development Environment:**

```bash
# Terminal 1: Backend
cd job-flow-backend
source venv/bin/activate
uvicorn app.main:app --reload

# Terminal 2: Extension watch mode
cd job-flow-extension
npm run watch
```

**2. Make Changes:**

- Edit source files in `src/`
- Watch mode auto-rebuilds
- Reload extension in chrome://extensions/

**3. Test Changes:**

- Navigate to test page
- Trigger auto-fill
- Check DevTools Console for logs
- Verify behavior

**4. Commit Changes:**

```bash
git add .
git commit -m "feat: Add new feature"
git push
```

### Release Process

**1. Version Bump:**

```bash
# Update version in manifest.json and package.json
# Follow semantic versioning: MAJOR.MINOR.PATCH
```

**2. Production Build:**

```bash
npm run build
```

**3. Test Production Build:**

- Load dist/ folder as unpacked extension
- Test all features
- Verify no console errors

**4. Package Extension:**

```bash
# Create ZIP for Chrome Web Store
cd dist
zip -r ../jobflow-extension-v1.0.0.zip .
```

**5. Tag Release:**

```bash
git tag v1.0.0
git push --tags
```

---

## Performance Optimization

### Bundle Size Analysis

```bash
# Install webpack bundle analyzer
npm install --save-dev webpack-bundle-analyzer

# Add to webpack.config.js
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;

plugins: [
  new BundleAnalyzerPlugin()
]

# Build and analyze
npm run build
```

### Code Splitting

Split large bundles:

```javascript
// Dynamic imports for platform handlers
const handler = await import(
  /* webpackChunkName: "linkedin-handler" */
  './platform-handlers/linkedin-handler'
);
```

### Lazy Loading

Load components on demand:

```typescript
// In popup/Popup.tsx
const AnalyticsDashboard = React.lazy(() =>
  import('./components/AnalyticsDashboard')
);

<React.Suspense fallback={<div>Loading...</div>}>
  <AnalyticsDashboard />
</React.Suspense>
```

---

## Best Practices

### Code Style

1. **Use TypeScript strictly:**
   ```typescript
   // Enable strict mode in tsconfig.json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true,
       "strictNullChecks": true
     }
   }
   ```

2. **Define interfaces for all data:**
   ```typescript
   interface FormField {
     id: string;
     label: string;
     type: FieldType;
     value: any;
     selector: string;
   }
   ```

3. **Use async/await consistently:**
   ```typescript
   async fillForm(fields: FormField[]): Promise<void> {
     for (const field of fields) {
       await this.fillField(field);
     }
   }
   ```

### Error Handling

```typescript
try {
  await this.fillField(field);
} catch (error) {
  logger.error('Failed to fill field', { field, error });
  // Continue with next field
}
```

### Testing Strategy

1. **Unit tests** for utilities and helpers
2. **Integration tests** for form detection
3. **Manual testing** for platform handlers
4. **E2E tests** for complete workflows (future)

---

## Resources

- [Chrome Extension Documentation](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 Migration Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)
- [Webpack Documentation](https://webpack.js.org/concepts/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [React Documentation](https://react.dev/)

---

**Last Updated:** Phase 3 - Platform Handler Integration
