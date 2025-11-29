# Tasks: Add AdminLTE Frontend Template Setup

## 1. Webpack Encore Setup

- [x] 1.1 Install symfony/webpack-encore-bundle via Composer
- [x] 1.2 Create package.json with npm init
- [x] 1.3 Install dev dependencies (@symfony/webpack-encore, webpack, webpack-cli, sass-loader, sass)
- [x] 1.4 Install AdminLTE dependencies (admin-lte@4, bootstrap, @popperjs/core)
- [x] 1.5 Create webpack.config.js with Encore configuration

## 2. Assets Structure

- [x] 2.1 Create `assets/app.js` entry point
- [x] 2.2 Create `assets/styles/app.scss` with AdminLTE imports
- [x] 2.3 Import Bootstrap and AdminLTE JS in app.js

## 3. Twig Templates

- [x] 3.1 Create `templates/base.html.twig` with AdminLTE layout
- [x] 3.2 Create `templates/components/_navbar.html.twig`
- [x] 3.3 Create `templates/components/_sidebar.html.twig`
- [x] 3.4 Create `templates/components/_footer.html.twig`
- [x] 3.5 Create `templates/home/index.html.twig` sample page

## 4. Controller

- [x] 4.1 Create `src/Controller/HomeController.php`
- [x] 4.2 Add route for index page (`/`)

## 5. Build and Test

- [x] 5.1 Run `npm run dev` to compile assets
- [x] 5.2 Verify page loads (HTTP 200)
- [x] 5.3 Verify AdminLTE styles are applied
- [x] 5.4 `npm run watch` script included by Encore bundle
