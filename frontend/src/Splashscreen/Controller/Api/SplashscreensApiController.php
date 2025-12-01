<?php

namespace App\Splashscreen\Controller\Api;

use App\Splashscreen\Service\SplashscreenService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Twig\Environment;

#[Route('/api/splashscreens')]
class SplashscreensApiController extends AbstractController
{
    public function __construct(
        private readonly SplashscreenService $splashscreenService,
        private readonly Environment $twig,
    ) {
    }

    /**
     * List all splashscreens with optional category filter.
     */
    #[Route('', name: 'api_splashscreens_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        $category = $request->query->get('category');
        $splashscreens = $this->splashscreenService->getByCategory($category);

        return new JsonResponse([
            'success' => true,
            'data' => array_map(fn($entity) => $entity->toArray(), $splashscreens),
        ]);
    }

    /**
     * Get a single splashscreen.
     */
    #[Route('/{id}', name: 'api_splashscreens_get', methods: ['GET'], requirements: ['id' => '\d+'])]
    public function get(int $id): JsonResponse
    {
        $splashscreen = $this->splashscreenService->find($id);

        if (!$splashscreen) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Splashscreen not found',
            ], Response::HTTP_NOT_FOUND);
        }

        return new JsonResponse([
            'success' => true,
            'data' => $splashscreen->toArray(),
        ]);
    }

    /**
     * Get raw SVG content for a splashscreen.
     */
    #[Route('/{id}/svg', name: 'api_splashscreens_get_svg', methods: ['GET'])]
    public function getSvg(int $id): Response
    {
        $splashscreen = $this->splashscreenService->find($id);

        if (!$splashscreen) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        $svgContent = $this->splashscreenService->getSvgForDisplay($splashscreen);

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

        $splashscreen = $this->splashscreenService->create(
            $data['name'],
            $data['category'],
            $data['svg_content']
        );

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

            $result = $this->splashscreenService->importSvg($svgContent, $baseName);

            return new JsonResponse([
                'success' => true,
                'message' => 'SVG imported successfully',
                'data' => [
                    'image' => $result['image']->toArray(),
                    'font' => $result['font']->toArray(),
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
        $splashscreen = $this->splashscreenService->find($id);

        if (!$splashscreen) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Splashscreen not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        $splashscreen = $this->splashscreenService->update(
            $splashscreen,
            $data['name'] ?? null,
            $data['svg_content'] ?? null
        );

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
        $splashscreen = $this->splashscreenService->find($id);

        if (!$splashscreen) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Splashscreen not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->splashscreenService->delete($splashscreen);

        return new JsonResponse([
            'success' => true,
            'message' => 'Splashscreen deleted',
        ]);
    }

    /**
     * Generate font preview SVG from raw content.
     */
    #[Route('/preview/font', name: 'api_splashscreens_preview_font', methods: ['POST'])]
    public function previewFont(Request $request): Response
    {
        $data = json_decode($request->getContent(), true);
        $fontContent = $data['svg_content'] ?? '';

        $previewSvg = $this->splashscreenService->generateFontPreview($fontContent);

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
        $images = $this->splashscreenService->getImages();

        $html = $this->twig->render('@Splashscreen/_tab_images.html.twig', [
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
        $fonts = $this->splashscreenService->getFonts();

        $html = $this->twig->render('@Splashscreen/_tab_fonts.html.twig', [
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

        $extension = strtolower($uploadedFile->getClientOriginalExtension());
        if (!in_array($extension, ['ttf', 'otf'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid file type. Must be TTF or OTF',
            ], Response::HTTP_BAD_REQUEST);
        }

        try {
            $font = $this->splashscreenService->importTtf($uploadedFile);

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
