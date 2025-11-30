<?php

namespace App\Controller\Api;

use App\Models\Splashscreen;
use App\Service\SvgParserService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\Contracts\HttpClient\HttpClientInterface;
use Twig\Environment;

#[Route('/api/splashscreens')]
class SplashscreensApiController extends AbstractController
{
    public function __construct(
        private readonly SvgParserService $svgParserService,
        private readonly HttpClientInterface $httpClient,
        private readonly Environment $twig,
    ) {
    }

    /**
     * List all splashscreens with optional category filter.
     */
    #[Route('', name: 'api_splashscreens_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        $query = Splashscreen::query()->orderBy('name');

        $category = $request->query->get('category');
        if ($category === 'image') {
            $query->images();
        } elseif ($category === 'font') {
            $query->fonts();
        }

        $splashscreens = $query->get();

        return new JsonResponse([
            'success' => true,
            'data' => $splashscreens->toArray(),
        ]);
    }

    /**
     * Get a single splashscreen.
     */
    #[Route('/{id}', name: 'api_splashscreens_get', methods: ['GET'], requirements: ['id' => '\d+'])]
    public function get(int $id): JsonResponse
    {
        $splashscreen = Splashscreen::find($id);

        if (!$splashscreen) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Splashscreen not found',
            ], Response::HTTP_NOT_FOUND);
        }

        // Include svg_content in response
        $data = $splashscreen->toArray();
        $data['svg_content'] = $splashscreen->getSvgContent();

        return new JsonResponse([
            'success' => true,
            'data' => $data,
        ]);
    }

    /**
     * Get raw SVG content for a splashscreen.
     */
    #[Route('/{id}/svg', name: 'api_splashscreens_get_svg', methods: ['GET'])]
    public function getSvg(int $id): Response
    {
        $splashscreen = Splashscreen::find($id);

        if (!$splashscreen) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        $svgContent = $splashscreen->getSvgContent();

        if ($splashscreen->category === 'font') {
            // Generate preview SVG for font (paths need <use> elements to be visible)
            // Pass font ID to ensure unique IDs and prevent conflicts when multiple fonts on page
            $svgContent = $this->svgParserService->generateFontPreview($svgContent, $id);
        } else {
            // Replace dimension placeholders for images
            $svgContent = $this->svgParserService->replaceDimensionPlaceholders($svgContent);
        }

        return new Response(
            $svgContent,
            Response::HTTP_OK,
            [
                'Content-Type' => 'image/svg+xml',
                'Cache-Control' => 'public, max-age=3600',
            ]
        );
    }

    /**
     * Create a new splashscreen.
     */
    #[Route('', name: 'api_splashscreens_create', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['name']) || empty(trim($data['name']))) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Name is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        if (!isset($data['category']) || !in_array($data['category'], ['image', 'font'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Category must be "image" or "font"',
            ], Response::HTTP_BAD_REQUEST);
        }

        if (!isset($data['svg_content']) || empty(trim($data['svg_content']))) {
            return new JsonResponse([
                'success' => false,
                'error' => 'SVG content is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        $splashscreen = new Splashscreen();
        $splashscreen->name = trim($data['name']);
        $splashscreen->category = $data['category'];
        $splashscreen->svg_content = $this->svgParserService->sanitize($data['svg_content']);
        $splashscreen->save();

        return new JsonResponse([
            'success' => true,
            'message' => 'Splashscreen created',
            'data' => $splashscreen->toArray(),
        ], Response::HTTP_CREATED);
    }

    /**
     * Import SVG file and create both image and font records.
     */
    #[Route('/import', name: 'api_splashscreens_import', methods: ['POST'])]
    public function import(Request $request): JsonResponse
    {
        $uploadedFile = $request->files->get('svg');

        if (!$uploadedFile) {
            return new JsonResponse([
                'success' => false,
                'error' => 'No SVG file provided',
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate MIME type
        $fileMime = $uploadedFile->getMimeType();
        if (!in_array($fileMime, ['image/svg+xml', 'text/xml', 'application/xml', 'text/plain'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid file type. Must be SVG',
            ], Response::HTTP_BAD_REQUEST);
        }

        try {
            $svgContent = file_get_contents($uploadedFile->getRealPath());
            $baseName = pathinfo($uploadedFile->getClientOriginalName(), PATHINFO_FILENAME);

            // Parse SVG and get data for both records
            $parsed = $this->svgParserService->parseForImport($svgContent, $baseName);

            // Create image record
            $image = new Splashscreen();
            $image->name = $parsed['image']['name'];
            $image->category = $parsed['image']['category'];
            $image->svg_content = $parsed['image']['svg_content'];
            $image->save();

            // Create font record
            $font = new Splashscreen();
            $font->name = $parsed['font']['name'];
            $font->category = $parsed['font']['category'];
            $font->svg_content = $parsed['font']['svg_content'];
            $font->save();

            return new JsonResponse([
                'success' => true,
                'message' => 'SVG imported successfully',
                'data' => [
                    'image' => $image->toArray(),
                    'font' => $font->toArray(),
                ],
            ], Response::HTTP_CREATED);
        } catch (\Exception $e) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Failed to import SVG: ' . $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Update an existing splashscreen.
     */
    #[Route('/{id}', name: 'api_splashscreens_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $splashscreen = Splashscreen::find($id);

        if (!$splashscreen) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Splashscreen not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        if (isset($data['name'])) {
            $splashscreen->name = trim($data['name']);
        }

        if (isset($data['svg_content'])) {
            $splashscreen->svg_content = $this->svgParserService->sanitize($data['svg_content']);
        }

        $splashscreen->save();

        return new JsonResponse([
            'success' => true,
            'message' => 'Splashscreen updated',
            'data' => $splashscreen->toArray(),
        ]);
    }

    /**
     * Delete a splashscreen.
     */
    #[Route('/{id}', name: 'api_splashscreens_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $splashscreen = Splashscreen::find($id);

        if (!$splashscreen) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Splashscreen not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $splashscreen->delete();

        return new JsonResponse([
            'success' => true,
            'message' => 'Splashscreen deleted',
        ]);
    }

    /**
     * Generate font preview SVG from raw content.
     * Used by the edit modal to show live preview of font paths.
     */
    #[Route('/preview/font', name: 'api_splashscreens_preview_font', methods: ['POST'])]
    public function previewFont(Request $request): Response
    {
        $data = json_decode($request->getContent(), true);
        $fontContent = $data['svg_content'] ?? '';

        if (empty(trim($fontContent))) {
            return new Response(
                '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50"><text x="10" y="30" fill="#666">No content</text></svg>',
                Response::HTTP_OK,
                ['Content-Type' => 'image/svg+xml']
            );
        }

        $previewSvg = $this->svgParserService->generateFontPreview($fontContent);

        return new Response(
            $previewSvg,
            Response::HTTP_OK,
            ['Content-Type' => 'image/svg+xml']
        );
    }

    /**
     * Get HTML content for images tab (lazy loading).
     */
    #[Route('/tab/images', name: 'api_splashscreens_tab_images', methods: ['GET'])]
    public function tabImages(): Response
    {
        $images = Splashscreen::images()->orderBy('name')->get();

        $html = $this->twig->render('splashscreens/_tab_images.html.twig', [
            'items' => $images,
        ]);

        return new Response($html, Response::HTTP_OK, ['Content-Type' => 'text/html']);
    }

    /**
     * Get HTML content for fonts tab (lazy loading).
     */
    #[Route('/tab/fonts', name: 'api_splashscreens_tab_fonts', methods: ['GET'])]
    public function tabFonts(): Response
    {
        $fonts = Splashscreen::fonts()->orderBy('name')->get();

        $html = $this->twig->render('splashscreens/_tab_fonts.html.twig', [
            'items' => $fonts,
        ]);

        return new Response($html, Response::HTTP_OK, ['Content-Type' => 'text/html']);
    }

    /**
     * Import TTF font file and convert to SVG paths via Python backend.
     */
    #[Route('/import/ttf', name: 'api_splashscreens_import_ttf', methods: ['POST'])]
    public function importTtf(Request $request): JsonResponse
    {
        $uploadedFile = $request->files->get('ttf');

        if (!$uploadedFile) {
            return new JsonResponse([
                'success' => false,
                'error' => 'No TTF file provided',
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate file extension
        $extension = strtolower($uploadedFile->getClientOriginalExtension());
        if (!in_array($extension, ['ttf', 'otf'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid file type. Must be TTF or OTF',
            ], Response::HTTP_BAD_REQUEST);
        }

        try {
            // Call Python backend for TTF conversion using multipart form data
            $formData = new \Symfony\Component\Mime\Part\Multipart\FormDataPart([
                'file' => \Symfony\Component\Mime\Part\DataPart::fromPath(
                    $uploadedFile->getRealPath(),
                    $uploadedFile->getClientOriginalName(),
                    $uploadedFile->getMimeType()
                ),
            ]);

            $response = $this->httpClient->request('POST', 'http://backend:8000/api/fonts/convert', [
                'headers' => $formData->getPreparedHeaders()->toArray(),
                'body' => $formData->bodyToIterable(),
            ]);

            $result = $response->toArray();

            if (!($result['success'] ?? false)) {
                return new JsonResponse([
                    'success' => false,
                    'error' => $result['detail'] ?? 'Font conversion failed',
                ], Response::HTTP_INTERNAL_SERVER_ERROR);
            }

            // Create font record
            $font = new Splashscreen();
            $font->name = $result['font_name'];
            $font->category = 'font';
            $font->svg_content = $result['svg_paths'];
            $font->save();

            return new JsonResponse([
                'success' => true,
                'message' => 'TTF font imported successfully',
                'data' => $font->toArray(),
            ], Response::HTTP_CREATED);
        } catch (\Exception $e) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Failed to import TTF: ' . $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}
