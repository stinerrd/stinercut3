# Change: Add AdminLTE Frontend Template Setup

## Why

The frontend Symfony application currently lacks a UI layer - no templates, assets, or build system. A consistent admin dashboard template is needed for the video editing interface. AdminLTE provides a complete Bootstrap 5-based admin template with sidebar navigation, cards, forms, and responsive layout.

## What Changes

- Install Webpack Encore for asset compilation
- Install AdminLTE 4 via npm (Bootstrap 5-based)
- Create base Twig template with AdminLTE layout structure
- Create reusable template components (sidebar, navbar, footer)
- Create sample HomeController and index page
- Configure SCSS compilation with AdminLTE imports

## Impact

- Affected specs: `frontend-templates` (new)
- Affected code:
  - `frontend/webpack.config.js` - Webpack Encore configuration
  - `frontend/package.json` - npm dependencies
  - `frontend/assets/` - JS and SCSS entry points
  - `frontend/templates/` - Twig template structure
  - `frontend/src/Controller/HomeController.php` - Sample controller
