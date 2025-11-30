<?php

namespace App\Controller\Api;

use App\Models\TandemMaster;
use App\Models\Setting;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/tandem-masters')]
class TandemMastersApiController extends AbstractController
{
    /**
     * List all tandem masters with optional active filter.
     */
    #[Route('', name: 'api_tandem_masters_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        $query = TandemMaster::query();

        if ($request->query->get('active') === 'true') {
            $query->where('active', true);
        }

        $tandemMasters = $query->get();

        return new JsonResponse([
            'success' => true,
            'data' => $tandemMasters->toArray(),
        ]);
    }

    /**
     * Get image binary for a tandem master.
     */
    #[Route('/{id}/image', name: 'api_tandem_masters_get_image', methods: ['GET'])]
    public function getImage(int $id): Response
    {
        $tandemMaster = TandemMaster::find($id);

        if (!$tandemMaster || !$tandemMaster->getImage()) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        return new Response(
            $tandemMaster->getImage(),
            Response::HTTP_OK,
            [
                'Content-Type' => $tandemMaster->getImageMime() ?? 'image/jpeg',
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

        $tandemMaster = new TandemMaster();
        $tandemMaster->name = trim($data['name']);
        $tandemMaster->active = $data['active'] ?? true;
        $tandemMaster->save();

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
        $tandemMaster = TandemMaster::find($id);

        if (!$tandemMaster) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Tandem master not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        if (isset($data['name'])) {
            $tandemMaster->name = trim($data['name']);
        }

        if (isset($data['active'])) {
            $tandemMaster->active = (bool) $data['active'];
        }

        $tandemMaster->save();

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
        $tandemMaster = TandemMaster::find($id);

        if (!$tandemMaster) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Tandem master not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $tandemMaster->delete();

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
        $tandemMaster = TandemMaster::find($id);

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

        // Validate file size
        $maxSize = Setting::get('avatar.max_upload_size', 5242880);
        if ($uploadedFile->getSize() > $maxSize) {
            return new JsonResponse([
                'success' => false,
                'error' => 'File size exceeds maximum allowed (' . ($maxSize / 1024 / 1024) . 'MB)',
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate MIME type
        $allowedMimes = ['image/jpeg', 'image/png', 'image/gif'];
        $fileMime = $uploadedFile->getMimeType();
        if (!in_array($fileMime, $allowedMimes)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid file type. Allowed: JPEG, PNG, GIF',
            ], Response::HTTP_BAD_REQUEST);
        }

        try {
            // Read image file
            $imageData = file_get_contents($uploadedFile->getRealPath());

            // Load image resource
            $image = imagecreatefromstring($imageData);
            if (!$image) {
                throw new \Exception('Failed to process image');
            }

            // Get target dimensions
            $targetWidth = Setting::get('avatar.width', 150);
            $targetHeight = Setting::get('avatar.height', 150);

            // Create resized image
            $resized = imagecreatetruecolor($targetWidth, $targetHeight);
            if (!$resized) {
                imagedestroy($image);
                throw new \Exception('Failed to create image resource');
            }

            // Resize and copy
            imagecopyresampled(
                $resized,
                $image,
                0,
                0,
                0,
                0,
                $targetWidth,
                $targetHeight,
                imagesx($image),
                imagesy($image)
            );

            // Convert to JPEG
            ob_start();
            imagejpeg($resized, null, 90);
            $jpegData = ob_get_clean();

            // Clean up
            imagedestroy($image);
            imagedestroy($resized);

            // Store in database
            $tandemMaster->image = $jpegData;
            $tandemMaster->image_mime = 'image/jpeg';
            $tandemMaster->save();

            return new JsonResponse([
                'success' => true,
                'message' => 'Avatar uploaded successfully',
                'data' => $tandemMaster->toArray(),
            ]);
        } catch (\Exception $e) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Failed to process image: ' . $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }
}
