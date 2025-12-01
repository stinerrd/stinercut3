<?php

namespace App\TandemMaster\Controller\Api;

use App\TandemMaster\Service\TandemMasterService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/tandem-masters')]
class TandemMastersApiController extends AbstractController
{
    public function __construct(
        private readonly TandemMasterService $tandemMasterService,
    ) {
    }

    /**
     * List all tandem masters with optional active filter.
     */
    #[Route('', name: 'api_tandem_masters_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        if ($request->query->get('active') === 'true') {
            $tandemMasters = $this->tandemMasterService->getActive();
        } else {
            $tandemMasters = $this->tandemMasterService->getAll();
        }

        return new JsonResponse([
            'success' => true,
            'data' => array_map(fn($tm) => $tm->toArray(), $tandemMasters),
        ]);
    }

    /**
     * Get image binary for a tandem master.
     */
    #[Route('/{id}/image', name: 'api_tandem_masters_get_image', methods: ['GET'])]
    public function getImage(int $id): Response
    {
        $imageData = $this->tandemMasterService->getImageData($id);

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
     * Create a new tandem master.
     */
    #[Route('', name: 'api_tandem_masters_create', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['name']) || empty(trim($data['name']))) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Name is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        $tandemMaster = $this->tandemMasterService->create(
            $data['name'],
            $data['active'] ?? true
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Tandem master created',
            'data' => $tandemMaster->toArray(),
        ], Response::HTTP_CREATED);
    }

    /**
     * Update an existing tandem master.
     */
    #[Route('/{id}', name: 'api_tandem_masters_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $tandemMaster = $this->tandemMasterService->find($id);

        if (!$tandemMaster) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Tandem master not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        $tandemMaster = $this->tandemMasterService->update(
            $tandemMaster,
            $data['name'] ?? null,
            isset($data['active']) ? (bool) $data['active'] : null
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Tandem master updated',
            'data' => $tandemMaster->toArray(),
        ]);
    }

    /**
     * Delete a tandem master.
     */
    #[Route('/{id}', name: 'api_tandem_masters_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $tandemMaster = $this->tandemMasterService->find($id);

        if (!$tandemMaster) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Tandem master not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->tandemMasterService->delete($tandemMaster);

        return new JsonResponse([
            'success' => true,
            'message' => 'Tandem master deleted',
        ]);
    }

    /**
     * Upload and process avatar image.
     */
    #[Route('/{id}/image', name: 'api_tandem_masters_upload_image', methods: ['POST'])]
    public function uploadImage(int $id, Request $request): JsonResponse
    {
        $tandemMaster = $this->tandemMasterService->find($id);

        if (!$tandemMaster) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Tandem master not found',
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
            $tandemMaster = $this->tandemMasterService->uploadImage($tandemMaster, $uploadedFile);

            return new JsonResponse([
                'success' => true,
                'message' => 'Avatar uploaded successfully',
                'data' => $tandemMaster->toArray(),
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
