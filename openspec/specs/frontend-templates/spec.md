# frontend-templates Specification

## Purpose
TBD - created by archiving change add-adminlte-frontend. Update Purpose after archive.
## Requirements
### Requirement: Base Template Layout

The frontend SHALL provide a base Twig template with AdminLTE layout structure.

#### Scenario: Base template provides AdminLTE wrapper
- **WHEN** a page extends `base.html.twig`
- **THEN** the page inherits AdminLTE wrapper structure
- **AND** includes compiled CSS from Webpack Encore
- **AND** includes compiled JS from Webpack Encore

#### Scenario: Base template includes navigation components
- **WHEN** a page extends `base.html.twig`
- **THEN** the page includes navbar component
- **AND** the page includes sidebar component
- **AND** the page includes footer component

#### Scenario: Base template provides content block
- **WHEN** a page extends `base.html.twig`
- **THEN** the page can override `{% block content %}` for page-specific content
- **AND** the page can override `{% block title %}` for page title

### Requirement: Webpack Encore Asset Compilation

The frontend SHALL use Webpack Encore for asset compilation.

#### Scenario: SCSS compilation
- **WHEN** `npm run dev` is executed
- **THEN** `assets/styles/app.scss` is compiled to CSS
- **AND** AdminLTE styles are included
- **AND** Bootstrap styles are included
- **AND** output is written to `public/build/`

#### Scenario: JavaScript bundling
- **WHEN** `npm run dev` is executed
- **THEN** `assets/app.js` is bundled
- **AND** AdminLTE JavaScript is included
- **AND** Bootstrap JavaScript is included
- **AND** Popper.js is included for dropdowns

#### Scenario: Watch mode for development
- **WHEN** `npm run watch` is executed
- **THEN** Webpack watches for file changes
- **AND** recompiles assets automatically on change

### Requirement: Sidebar Navigation

The frontend sidebar SHALL provide navigation menu structure.

#### Scenario: Sidebar displays application branding
- **WHEN** sidebar is rendered
- **THEN** application name/logo is displayed at top

#### Scenario: Sidebar supports menu items
- **WHEN** sidebar is rendered
- **THEN** navigation links are displayed
- **AND** active page is highlighted

### Requirement: Home Page

The frontend SHALL provide a default home page.

#### Scenario: Home page accessible at root URL
- **WHEN** user navigates to `/`
- **THEN** HomeController renders home/index.html.twig
- **AND** page displays within AdminLTE layout

