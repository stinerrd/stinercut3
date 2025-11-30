# Design: AdminLTE Frontend Template Setup

## Context

The Tandem Video Editor frontend is a Symfony 7.2 application that currently has:
- PHP dependencies installed
- Eloquent ORM models defined
- Configuration files in place

But lacks:
- Templates directory (no UI)
- Assets directory (no CSS/JS)
- Webpack Encore (no build system)
- Controllers (empty directory)

## Goals / Non-Goals

**Goals:**
- Establish a complete frontend build pipeline with Webpack Encore
- Integrate AdminLTE 4 admin dashboard template
- Create reusable Twig template structure
- Enable SCSS compilation for customization
- Provide working sample page to verify setup

**Non-Goals:**
- Implementing actual video editing UI (future work)
- Adding all AdminLTE plugins (add as needed)
- Custom theming (use AdminLTE defaults initially)

## Decisions

### Decision 1: AdminLTE 4 via npm
**What:** Install AdminLTE 4 as npm dependency, import via Webpack Encore
**Why:**
- AdminLTE 4 is Bootstrap 5-based (modern, no jQuery required)
- npm installation allows version control and updates
- Webpack Encore can tree-shake unused components
- SCSS source allows customization

**Alternatives considered:**
- CDN links: No customization, external dependency
- Copy static files: Version updates difficult
- AdminLTE 3: Requires jQuery, Bootstrap 4

### Decision 2: Component-based Twig Structure
**What:** Split layout into reusable partials (_sidebar, _navbar, _footer)
**Why:**
- DRY principle - components used across all pages
- Easy to modify individual sections
- Follows Symfony best practices
- Enables future page-specific customization

### Decision 3: Single Entry Point
**What:** One `app.js` and `app.scss` entry point
**Why:**
- Simple initial setup
- All pages share same base styles/scripts
- Can add page-specific entries later if needed
- Reduces complexity for video editing SPA-like UI

## Architecture

```
frontend/
├── assets/
│   ├── app.js              # Main JS entry
│   │   └── imports AdminLTE JS, Bootstrap
│   └── styles/
│       └── app.scss        # Main SCSS entry
│           └── imports AdminLTE SCSS, Bootstrap
├── templates/
│   ├── base.html.twig      # Master layout
│   │   ├── DOCTYPE, meta, Encore CSS
│   │   ├── AdminLTE wrapper structure
│   │   ├── {% include '_navbar.html.twig' %}
│   │   ├── {% include '_sidebar.html.twig' %}
│   │   ├── {% block content %}{% endblock %}
│   │   ├── {% include '_footer.html.twig' %}
│   │   └── Encore JS
│   ├── components/
│   │   ├── _navbar.html.twig
│   │   ├── _sidebar.html.twig
│   │   └── _footer.html.twig
│   └── home/
│       └── index.html.twig  # Sample page
└── public/
    └── build/               # Webpack output (gitignored)
```

## AdminLTE Layout Structure

AdminLTE 4 requires specific wrapper div structure:
```html
<body class="hold-transition sidebar-mini">
  <div class="wrapper">
    <!-- Navbar -->
    <nav class="main-header navbar navbar-expand navbar-white navbar-light">

    <!-- Main Sidebar -->
    <aside class="main-sidebar sidebar-dark-primary elevation-4">

    <!-- Content Wrapper -->
    <div class="content-wrapper">
      <!-- Content Header -->
      <div class="content-header">
      <!-- Main content -->
      <section class="content">

    <!-- Footer -->
    <footer class="main-footer">
  </div>
</body>
```

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| AdminLTE version updates | Pin version in package.json |
| Large bundle size | Tree-shaking via Webpack, add plugins on-demand |
| SCSS compilation errors | Test build after each change |
| Template inheritance issues | Follow Symfony Twig best practices |

## Migration Plan

1. Install Webpack Encore bundle via Composer
2. Initialize npm and install dependencies
3. Create webpack.config.js with SCSS support
4. Create assets entry points
5. Create Twig templates
6. Create HomeController
7. Run `npm run dev` to compile
8. Test in browser

**Rollback:** Remove assets/, templates/, webpack.config.js, package.json
