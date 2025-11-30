## 1. Backend Controller Infrastructure

- [x] 1.1 Create `frontend/src/Controller/AppController.php` with:
  - Private arrays for `$jsGlobals` and `$pageJavascripts`
  - `addJs(string $path)` method to add page-specific JS files
  - `addJsVar(string $key, mixed $value)` method to add global JS variables
  - Override `render()` to merge `js_vars_global` and `page_javascripts` into template parameters

- [x] 1.2 Update `frontend/src/Controller/HomeController.php`:
  - Extend `AppController` instead of `AbstractController`
  - Call `$this->addJs('js/detector-status.js')` in `index()` method
  - Call `$this->addJsVar('backendApiUrl', '/api/services/detector')` in `index()` method

## 2. Template Updates

- [x] 2.1 Update `frontend/templates/base.html.twig`:
  - Add `window.App` initialization script block before closing `</body>`
  - Add `{% block javascripts %}` to load page-specific JS files via `page_javascripts` variable
  - Use `{{ asset() }}` for JS file paths

- [x] 2.2 Update `frontend/templates/home/index.html.twig`:
  - Add detector status card in dashboard grid (col-lg-4)
  - Include service status badge element (`#detector-service-status`)
  - Include listener toggle switch (`#detector-listener-toggle`)
  - Include error message area (`#detector-error`)
  - Include refresh indicator (`#detector-refresh-indicator`)

## 3. JavaScript Implementation

- [x] 3.1 Create `frontend/public/js/detector-status.js`:
  - IIFE pattern with 'use strict'
  - Read `window.App.backendApiUrl` for API base URL
  - Define POLL_INTERVAL constant (5000ms)
  - Initialize DOM element references on DOMContentLoaded
  - Implement `fetchStatus()` function with fetch API
  - Implement `handleToggle(e)` function for switch changes
  - Implement `updateUI(data)` function to update DOM
  - Implement `showToast(message, type)` function for notifications
  - Start polling interval on init

## 4. Styling

- [x] 4.1 Add CSS spin animation for refresh indicator:
  - Add `.spin` class with rotate keyframes
  - Can be inline in template or added to `app.scss`

## 5. Validation

- [x] 5.1 Test detector status display:
  - Verify "Running" badge when detector is up
  - Verify "Offline" badge when detector is down
  - Verify auto-refresh updates status

- [x] 5.2 Test listener toggle:
  - Verify toggle enables monitoring (POST to /enable)
  - Verify toggle disables monitoring (POST to /disable)
  - Verify error toast on failure
  - Verify toggle reverts on error

- [x] 5.3 Build and verify:
  - Run `npm run dev` in frontend container
  - Verify no JS console errors
  - Verify API calls work through proxy
