<?php

namespace App\Service;

use App\Models\Splashscreen;
use DOMDocument;
use DOMXPath;

class SvgParserService
{
    private const FONT_PLACEHOLDER = '[[[FONT]]]';
    private const WIDTH_PLACEHOLDER = '[[[WIDTH]]]';
    private const HEIGHT_PLACEHOLDER = '[[[HEIGHT]]]';

    /**
     * Extract all font paths (id="_A", "_B", "_Ouml", etc.) from SVG content.
     *
     * @param string $svgContent Full SVG content
     * @return string SVG fragment containing only font path elements
     */
    public function extractFontPaths(string $svgContent): string
    {
        $dom = new DOMDocument();
        $dom->preserveWhiteSpace = false;
        @$dom->loadXML($svgContent, LIBXML_NONET);

        $xpath = new DOMXPath($dom);
        $xpath->registerNamespace('svg', 'http://www.w3.org/2000/svg');

        // Valid umlaut ID suffixes
        $umlautIds = ['Ouml', 'Auml', 'Uuml', 'ouml', 'auml', 'uuml', 'szlig'];

        // Find all elements with id matching pattern _A, _B, _a, _b, _0, _1, _Ouml, _szlig, etc.
        $fontPaths = [];
        $allElements = $xpath->query('//*[@id]');

        foreach ($allElements as $element) {
            $id = $element->getAttribute('id');
            // Match pattern: underscore followed by single alphanumeric char OR umlaut name
            if (preg_match('/^_[A-Za-z0-9]$/', $id)) {
                $fontPaths[] = $dom->saveXML($element);
            } elseif (preg_match('/^_(.+)$/', $id, $matches) && in_array($matches[1], $umlautIds, true)) {
                $fontPaths[] = $dom->saveXML($element);
            }
        }

        return implode("\n", $fontPaths);
    }

    /**
     * Extract image content (everything except font paths) and insert placeholder.
     *
     * @param string $svgContent Full SVG content
     * @return string SVG content with font paths replaced by [[[FONT]]] placeholder
     */
    public function extractImageContent(string $svgContent): string
    {
        $dom = new DOMDocument();
        $dom->preserveWhiteSpace = false;
        $dom->formatOutput = true;
        @$dom->loadXML($svgContent, LIBXML_NONET);

        $xpath = new DOMXPath($dom);
        $xpath->registerNamespace('svg', 'http://www.w3.org/2000/svg');

        // Valid umlaut ID suffixes
        $umlautIds = ['Ouml', 'Auml', 'Uuml', 'ouml', 'auml', 'uuml', 'szlig'];

        // Find all font elements and remove them
        $fontElements = [];
        $allElements = $xpath->query('//*[@id]');

        foreach ($allElements as $element) {
            $id = $element->getAttribute('id');
            // Match single char IDs OR umlaut IDs
            if (preg_match('/^_[A-Za-z0-9]$/', $id)) {
                $fontElements[] = $element;
            } elseif (preg_match('/^_(.+)$/', $id, $matches) && in_array($matches[1], $umlautIds, true)) {
                $fontElements[] = $element;
            }
        }

        // Get the parent of first font element to insert placeholder
        $placeholderInserted = false;
        foreach ($fontElements as $element) {
            $parent = $element->parentNode;
            if (!$placeholderInserted && $parent) {
                // Create a comment as placeholder marker
                $placeholder = $dom->createComment(self::FONT_PLACEHOLDER);
                $parent->insertBefore($placeholder, $element);
                $placeholderInserted = true;
            }
            $parent->removeChild($element);
        }

        $result = $dom->saveXML();

        // Replace comment with actual placeholder text
        $result = str_replace('<!--' . self::FONT_PLACEHOLDER . '-->', self::FONT_PLACEHOLDER, $result);

        return $result;
    }

    /**
     * Sanitize SVG content by removing potentially dangerous elements.
     *
     * @param string $svgContent SVG content to sanitize
     * @return string Sanitized SVG content
     */
    public function sanitize(string $svgContent): string
    {
        $dom = new DOMDocument();
        $dom->preserveWhiteSpace = false;
        @$dom->loadXML($svgContent, LIBXML_NONET);

        $xpath = new DOMXPath($dom);

        // Remove script elements
        $scripts = $xpath->query('//script');
        foreach ($scripts as $script) {
            $script->parentNode->removeChild($script);
        }

        // Remove event attributes (onclick, onload, etc.)
        $allElements = $xpath->query('//*');
        foreach ($allElements as $element) {
            $attributesToRemove = [];
            foreach ($element->attributes as $attr) {
                if (preg_match('/^on/i', $attr->name)) {
                    $attributesToRemove[] = $attr->name;
                }
            }
            foreach ($attributesToRemove as $attrName) {
                $element->removeAttribute($attrName);
            }
        }

        return $dom->saveXML();
    }

    /**
     * Assemble final SVG by combining image and font content.
     *
     * @param Splashscreen $image Image element with [[[FONT]]] placeholder
     * @param Splashscreen $font Font element with path definitions
     * @return string Complete SVG content
     */
    public function assembleSvg(Splashscreen $image, Splashscreen $font): string
    {
        $imageContent = $image->getSvgContent();
        $fontContent = $font->getSvgContent();

        return str_replace(self::FONT_PLACEHOLDER, $fontContent, $imageContent);
    }

    /**
     * Parse SVG file and create both image and font records.
     *
     * @param string $svgContent Full SVG content
     * @param string $baseName Base name for the records
     * @return array{image: array, font: array} Data for creating both records
     */
    public function parseForImport(string $svgContent, string $baseName): array
    {
        $sanitized = $this->sanitize($svgContent);

        return [
            'image' => [
                'name' => $baseName,
                'category' => 'image',
                'svg_content' => $this->extractImageContent($sanitized),
            ],
            'font' => [
                'name' => $baseName . ' Font',
                'category' => 'font',
                'svg_content' => $this->extractFontPaths($sanitized),
            ],
        ];
    }

    /**
     * Replace dimension placeholders with actual values from viewBox.
     *
     * SVG files may contain [[[WIDTH]]] and [[[HEIGHT]]] placeholders
     * that need to be replaced with actual dimensions for display.
     *
     * @param string $svgContent SVG content with potential placeholders
     * @return string SVG content with placeholders replaced
     */
    public function replaceDimensionPlaceholders(string $svgContent): string
    {
        // Extract width and height from viewBox (format: "minX minY width height")
        if (preg_match('/viewBox\s*=\s*"[^\s"]+\s+[^\s"]+\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)"/', $svgContent, $matches)) {
            $width = (int) $matches[1];
            $height = (int) $matches[2];
        } else {
            // Default to Full HD if viewBox not found
            $width = 1920;
            $height = 1080;
        }

        $svgContent = str_replace(self::WIDTH_PLACEHOLDER, (string) $width, $svgContent);
        $svgContent = str_replace(self::HEIGHT_PLACEHOLDER, (string) $height, $svgContent);

        return $svgContent;
    }

    // Mapping of special character IDs to display order within their groups
    private const UMLAUT_IDS = [
        // Uppercase umlauts (display after regular uppercase)
        'Auml' => 'upper',   // Ä
        'Ouml' => 'upper',   // Ö
        'Uuml' => 'upper',   // Ü
        // Lowercase umlauts (display after regular lowercase)
        'auml' => 'lower',   // ä
        'ouml' => 'lower',   // ö
        'uuml' => 'lower',   // ü
        'szlig' => 'lower',  // ß
    ];

    /**
     * Generate a preview SVG for font content.
     *
     * Font records only contain path definitions (e.g., <path id="_A">).
     * This method creates a complete SVG that displays all available letters
     * using <use> elements to reference the path definitions.
     *
     * Layout: Multiple rows - uppercase, lowercase, digits, umlauts
     *
     * @param string $fontContent Font path definitions
     * @param int|null $fontId Optional font ID for unique prefixing (prevents ID conflicts when multiple fonts on page)
     * @return string Complete SVG with visible font preview
     */
    public function generateFontPreview(string $fontContent, ?int $fontId = null): string
    {
        // Generate unique prefix for this font to avoid ID conflicts when multiple SVGs on same page
        $prefix = $fontId !== null ? "f{$fontId}_" : 'f' . uniqid() . '_';

        // Add prefix to all IDs in the font content (single char OR umlaut names like Ouml, szlig)
        $prefixedContent = preg_replace('/id="(_[A-Za-z0-9]+)"/', 'id="' . $prefix . '$1"', $fontContent);

        // Extract all letter IDs from path definitions (now with prefix)
        // Match single chars (A-Z, a-z, 0-9) and umlaut names (Ouml, auml, szlig, etc.)
        preg_match_all('/id="(' . preg_quote($prefix, '/') . '_[A-Za-z0-9]+)"/', $prefixedContent, $matches);
        $letterIds = array_unique($matches[1]);

        if (empty($letterIds)) {
            return '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50"><text x="10" y="30" fill="#666">No font letters found</text></svg>';
        }

        // Group letters by type
        $uppercase = [];
        $lowercase = [];
        $digits = [];
        $upperUmlauts = [];
        $lowerUmlauts = [];

        foreach ($letterIds as $id) {
            // Extract character/name from prefixed ID (e.g., "f12__A" -> "A", "f12__Ouml" -> "Ouml")
            $charOrName = preg_replace('/^' . preg_quote($prefix, '/') . '_/', '', $id);

            // Check if it's an umlaut ID
            if (isset(self::UMLAUT_IDS[$charOrName])) {
                if (self::UMLAUT_IDS[$charOrName] === 'upper') {
                    $upperUmlauts[] = $id;
                } else {
                    $lowerUmlauts[] = $id;
                }
            } elseif (strlen($charOrName) === 1) {
                // Single character
                $char = $charOrName;
                if (ctype_upper($char)) {
                    $uppercase[] = $id;
                } elseif (ctype_lower($char)) {
                    $lowercase[] = $id;
                } elseif (ctype_digit($char)) {
                    $digits[] = $id;
                }
            }
        }

        sort($uppercase);
        sort($lowercase);
        sort($digits);
        sort($upperUmlauts);
        sort($lowerUmlauts);

        // Layout settings (in output pixels)
        $startX = 10;
        $letterWidth = 80;
        $letterGap = 8;
        $rowHeight = 100;
        $maxPerRow = 7;

        $uses = '';
        $y = 50;
        $maxWidth = 100;

        // Helper function to render a group of letters
        $renderGroup = function (array $letters) use (&$uses, &$y, &$maxWidth, $startX, $letterWidth, $letterGap, $rowHeight, $maxPerRow) {
            if (empty($letters)) {
                return;
            }

            $x = $startX;
            $count = 0;

            foreach ($letters as $id) {
                // Start new row after maxPerRow letters
                if ($count > 0 && $count % $maxPerRow === 0) {
                    $maxWidth = max($maxWidth, $x);
                    $y += $rowHeight;
                    $x = $startX;
                }

                $uses .= sprintf(
                    '<use xlink:href="#%s" transform="translate(%d %d)" fill="#333" />',
                    htmlspecialchars($id, ENT_XML1),
                    $x,
                    $y
                );
                $x += $letterWidth + $letterGap;
                $count++;
            }

            $maxWidth = max($maxWidth, $x);
            $y += $rowHeight; // Move to next row for next group
        };

        // Render each group on separate rows
        // Uppercase letters followed by uppercase umlauts (ÄÖÜ)
        $renderGroup(array_merge($uppercase, $upperUmlauts));
        // Lowercase letters followed by lowercase umlauts (äöüß)
        $renderGroup(array_merge($lowercase, $lowerUmlauts));
        $renderGroup($digits);

        // Final dimensions
        $width = $maxWidth + 10;
        $height = $y + 10;

        // Build complete SVG
        return sprintf(
            '<?xml version="1.0" encoding="UTF-8"?>' .
            '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ' .
            'viewBox="0 0 %d %d" width="%d" height="%d">' .
            '<defs>%s</defs>%s</svg>',
            $width,
            $height,
            $width,
            $height,
            $prefixedContent,
            $uses
        );
    }
}
