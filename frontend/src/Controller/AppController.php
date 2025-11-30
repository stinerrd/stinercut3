<?php

namespace App\Controller;

use InvalidArgumentException;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;

/**
 * Abstract base controller for all web controllers.
 *
 * Provides methods to inject page-specific JavaScript files and global
 * JavaScript variables into templates.
 *
 * Usage:
 * - $this->addJs('js/my-script.js') - Add page-specific JS file
 * - $this->addJsVar('key', 'value') - Add JS variable (window.App.key)
 */
abstract class AppController extends AbstractController
{
    private array $jsGlobals = [];
    private array $pageJavascripts = [];

    public function __construct()
    {
        // Add default global JS variables
        // WebSocket connects directly to backend port (no SSL/Traefik)
        $this->addJsVar('websocketUrl', $_ENV['WEBSOCKET_URL'] ?? 'ws://localhost:8002/ws');
    }

    /**
     * Renders a view with automatic injection of JavaScript configuration.
     */
    protected function render(string $view, array $parameters = [], Response $response = null): Response
    {
        $parameters = array_merge($parameters, [
            'js_vars_global' => $this->jsGlobals,
            'page_javascripts' => $this->pageJavascripts,
        ]);

        return parent::render($view, $parameters, $response);
    }

    /**
     * Add a global JavaScript variable (available as window.App.key).
     */
    protected function addJsVar(string $key, mixed $value): void
    {
        if (!preg_match('/^[a-zA-Z_][a-zA-Z0-9_]*$/', $key)) {
            throw new InvalidArgumentException("Invalid JS variable key: $key");
        }

        $this->jsGlobals[$key] = json_encode($value);
    }

    /**
     * Add a page-specific JavaScript file to be loaded.
     *
     * @param string $path Path relative to public/ (e.g., 'js/detector-status.js')
     */
    protected function addJs(string $path): void
    {
        if (!in_array($path, $this->pageJavascripts, true)) {
            $this->pageJavascripts[] = $path;
        }
    }
}
