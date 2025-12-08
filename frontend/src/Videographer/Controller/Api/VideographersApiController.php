<?php

namespace App\Videographer\Controller\Api;

use App\Videographer\Service\VideographerService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/videographers')]
class VideographersApiController extends AbstractController
{
    public function __construct(
        private readonly VideographerService $videographerService,
    ) {
    }

    /**
     * List all videographers with optional active filter.
     */
    #[Route('', name: 'api_videographers_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        if ($request->query->get('active') === 'true') {
            $videographers = $this->videographerService->getActive();
        } else {
            $videographers = $this->videographerService->getAll();
        }

        return new JsonResponse([
            'success' => true,
            'data' => array_map(fn($v) => $v->toArray(), $videographers),
        ]);
    }

    /**
     * Get image binary for a videographer.
     */
    #[Route('/{id}/image', name: 'api_videographers_get_image', methods: ['GET'])]
    public function getImage(int $id): Response
    {
        $imageData = $this->videographerService->getImageData($id);

        if (!$imageData) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        return new Response(
            $imageData['data'],
            Response::HTTP_OK,
            [
                'Content-Type' => $imageData['mime'],
                'Cache-Control' => 'public, max-age=3600',
            ]
        );
    }

    /**
     * Create a new videographer.
     */
    #[Route('', name: 'api_videographers_create', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['name']) || empty(trim($data['name']))) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Name is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        $videographer = $this->videographerService->create(
            $data['name'],
            $data['active'] ?? true
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Videographer created',
            'data' => $videographer->toArray(),
        ], Response::HTTP_CREATED);
    }

    /**
     * Update an existing videographer.
     */
    #[Route('/{id}', name: 'api_videographers_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $videographer = $this->videographerService->find($id);

        if (!$videographer) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Videographer not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        $videographer = $this->videographerService->update(
            $videographer,
            $data['name'] ?? null,
            isset($data['active']) ? (bool) $data['active'] : null
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Videographer updated',
            'data' => $videographer->toArray(),
        ]);
    }

    /**
     * Delete a videographer.
     */
    #[Route('/{id}', name: 'api_videographers_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $videographer = $this->videographerService->find($id);

        if (!$videographer) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Videographer not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->videographerService->delete($videographer);

        return new JsonResponse([
            'success' => true,
            'message' => 'Videographer deleted',
        ]);
    }

    /**
     * Upload and process avatar image.
     */
    #[Route('/{id}/image', name: 'api_videographers_upload_image', methods: ['POST'])]
    public function uploadImage(int $id, Request $request): JsonResponse
    {
        $videographer = $this->videographerService->find($id);

        if (!$videographer) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Videographer not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $uploadedFile = $request->files->get('image');

        if (!$uploadedFile) {
            return new JsonResponse([
                'success' => false,
                'error' => 'No image file provided',
            ], Response::HTTP_BAD_REQUEST);
        }

        try {
            $videographer = $this->videographerService->uploadImage($videographer, $uploadedFile);

            return new JsonResponse([
                'success' => true,
                'message' => 'Avatar uploaded successfully',
                'data' => $videographer->toArray(),
            ]);
        } catch (\InvalidArgumentException $e) {
            return new JsonResponse([
                'success' => false,
                'error' => $e->getMessage(),
            ], Response::HTTP_BAD_REQUEST);
        } catch (\Exception $e) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Failed to process image: ' . $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}
