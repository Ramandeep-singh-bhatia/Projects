# JobFlow Chrome Extension

Chrome extension for JobFlow - automated job application form filling.

## Features

- ✅ Automatic form detection on job application pages
- ✅ Smart field mapping with fuzzy matching
- ✅ One-click form filling
- ✅ Real-time backend synchronization
- ✅ Keyboard shortcuts (Ctrl+Shift+F)
- ✅ Visual notifications
- 🚧 LinkedIn Easy Apply support (coming soon)
- 🚧 Multi-platform handlers (Workday, Greenhouse, etc.) (coming soon)

## Installation

### Prerequisites

- Node.js 18+
- JobFlow backend running at http://localhost:8000

### Setup

```bash
# Install dependencies
npm install

# Build extension
npm run build

# Or build in development mode with watch
npm run dev
```

### Load in Chrome

1. Open Chrome and navigate to `chrome://extensions`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `job-flow-extension/dist` folder
5. The extension should now appear in your extensions list

## Development

```bash
# Build in development mode (unminified, with source maps)
npm run build:dev

# Watch mode (rebuilds on file changes)
npm run dev

# Type checking
npm run type-check
```

## Project Structure

```
src/
├── background/
│   └── service-worker.ts         # Background service worker
├── content/
│   ├── content-script.ts         # Main content script
│   ├── form-detector.ts          # Form detection logic
│   └── field-mapper.ts           # Field to data mapping
├── popup/
│   └── Popup.tsx                 # Extension popup UI
├── options/
│   └── Options.tsx               # Settings page
└── shared/
    ├── types/                    # TypeScript types
    ├── api/                      # Backend API client
    └── utils/                    # Utilities (storage, logger)
```

## Usage

1. **Configure Backend**
   - Click extension icon → Settings
   - Ensure backend URL is correct (default: http://localhost:8000)
   - Test connection

2. **Navigate to Job Application**
   - Go to any job application page (LinkedIn, Workday, etc.)
   - Extension will automatically detect forms

3. **Fill Form**
   - Click extension icon
   - Click "Fill Form" button
   - Or use keyboard shortcut: `Ctrl+Shift+F` (Windows/Linux) or `Cmd+Shift+F` (Mac)

4. **Review and Submit**
   - Review pre-filled data
   - Make any necessary edits
   - Submit application manually

## Keyboard Shortcuts

- `Ctrl+Shift+F` (or `Cmd+Shift+F` on Mac) - Fill current form

## Supported Platforms

### Currently Supported
- Generic forms (any website with standard HTML forms)

### Coming Soon
- LinkedIn Easy Apply
- Workday ATS
- Greenhouse ATS
- Lever ATS
- Taleo ATS
- iCIMS ATS

## Configuration

Settings are accessible via:
- Extension icon → Settings button
- Or right-click extension icon → Options

Available settings:
- **Backend URL** - API server location
- **Auto-fill enabled** - Enable/disable automatic filling
- **Show review interface** - Show review before submit
- **Keyboard shortcuts** - Enable/disable hotkeys
- **Notifications** - Show/hide notifications

## API Communication

The extension communicates with the backend via:
- REST API for data retrieval (profile, questions, resumes)
- Chrome storage for caching
- Message passing between content script and background

## Troubleshooting

### Extension not detecting forms
- Refresh the page
- Check if you're on a job application page
- Open console (F12) and look for JobFlow logs

### Backend connection failed
- Ensure backend is running: `uvicorn app.main:app --reload`
- Check backend URL in settings
- Verify CORS is configured correctly in backend

### Form filling not working
- Ensure profile is set up in backend
- Check console for errors
- Try disabling and re-enabling the extension

## Security & Privacy

- All data is stored locally or on your own backend
- No data is sent to external servers
- No tracking or analytics
- Open source - review the code yourself

## Contributing

This extension is part of the JobFlow project. See main README for contribution guidelines.

## License

MIT License
