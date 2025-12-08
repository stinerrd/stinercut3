<?php

namespace App\Media\Controller\Api;

use App\Media\Service\VideopartService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\Routing\Attribute\Route;
use Twig\Environment;

#[Route('/api/videoparts')]
class VideopartsApiController extends AbstractController
{
    public function __construct(
        private readonly VideopartService $videopartService,
        private readonly Environment $twig,
    ) {
    }

    /**
     * List all videoparts with optional type filter.
     */
    #[Route('', name: 'api_videoparts_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        $type = $request->query->get('type');
        $videoparts = $this->videopartService->getByType($type);

        return new JsonResponse([
            'success' => true,
            'data' => array_map(fn($entity) => $entity->toArray(), $videoparts),
        ]);
    }

    /**
     * Get a single videopart.
     */
    #[Route('/{id}', name: 'api_videoparts_get', methods: ['GET'], requirements: ['id' => '\d+'])]
    public function get(int $id): JsonResponse
    {
        $videopart = $this->videopartService->find($id);

        if (!$videopart) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Videopart not found',
            ], Response::HTTP_NOT_FOUND);
        }

        return new JsonResponse([
            'success' => true,
            'data' => $videopart->toArray(),
        ]);
    }

    /**
     * Upload a new video file.
     */
    #[Route('/upload', name: 'api_videoparts_upload', methods: ['POST'])]
    public function upload(Request $request): JsonResponse
    {
        $uploadedFile = $request->files->get('video');

        if (!$uploadedFile) {
            return new JsonResponse([
                'success' => false,
                'error' => 'No video file provided',
            ], Response::HTTP_BAD_REQUEST);
        }

        $type = $request->request->get('type');
        if (!$type || !in_array($type, ['intro', 'outro'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Type must be "intro" or "outro"',
            ], Response::HTTP_BAD_REQUEST);
        }

        $name = $request->request->get('name');
        $description = $request->request->get('description');

        try {
            $videopart = $this->videopartService->uploadVideo(
                $uploadedFile,
                $type,
                $name,
                $description
            );

            return new JsonResponse([
                'success' => true,
                'message' => 'Video uploaded successfully',
                'data' => $videopart->toArray(),
            ], Response::HTTP_CREATED);
        } catch (\InvalidArgumentException $e) {
            return new JsonResponse([
                'success' => false,
                'error' => $e->getMessage(),
            ], Response::HTTP_BAD_REQUEST);
        } catch (\Exception $e) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Failed to upload video: ' . $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Update an existing videopart.
     */
    #[Route('/{id}', name: 'api_videoparts_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $videopart = $this->videopartService->find($id);

        if (!$videopart) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Videopart not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        $videopart = $this->videopartService->update(
            $videopart,
            $data['name'] ?? null,
            $data['description'] ?? null
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Videopart updated',
            'data' => $videopart->toArray(),
        ]);
    }

    /**
     * Delete a videopart.
     */
    #[Route('/{id}', name: 'api_videoparts_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $videopart = $this->videopartService->find($id);

        if (!$videopart) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Videopart not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->videopartService->delete($videopart);

        return new JsonResponse([
            'success' => true,
            'message' => 'Videopart deleted',
        ]);
    }

    /**
     * Get thumbnail image for a videopart.
     */
    #[Route('/{id}/thumbnail', name: 'api_videoparts_thumbnail', methods: ['GET'])]
    public function thumbnail(int $id): Response
    {
        $thumbnail = $this->videopartService->getThumbnail($id);

        if (!$thumbnail) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        return new Response(
            $thumbnail,
            Response::HTTP_OK,
            [
                'Content-Type' => 'image/jpeg',
                'Cache-Control' => 'public, max-age=3600',
            ]
        );
    }

    /**
     * Stream video file for preview playback.
     */
    #[Route('/{id}/video', name: 'api_videoparts_video', methods: ['GET'])]
    public function video(int $id): Response
    {
        $videopart = $this->videopartService->find($id);

        if (!$videopart) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        $filePath = $this->videopartService->getFullFilePath($videopart);

        if (!file_exists($filePath)) {
            return new Response('Video file not found', Response::HTTP_NOT_FOUND);
        }

        $extension = strtolower(pathinfo($filePath, PATHINFO_EXTENSION));
        $mimeType = match ($extension) {
            'mov' => 'video/quicktime',
            default => 'video/mp4',
        };

        $response = new BinaryFileResponse($filePath);
        $response->headers->set('Content-Type', $mimeType);
        $response->headers->set('Accept-Ranges', 'bytes');
        $response->headers->set('Cache-Control', 'public, max-age=3600');
        $response->setContentDisposition(ResponseHeaderBag::DISPOSITION_INLINE, $videopart->getName() . '.' . $extension);

        return $response;
    }

    /**
     * Get HTML content for videoparts tab (lazy loading).
     */
    #[Route('/tab/content', name: 'api_videoparts_tab', methods: ['GET'])]
    public function tabContent(): Response
    {
        $videoparts = $this->videopartService->getAll();

        $html = $this->twig->render('@Media/_tab_videoparts.html.twig', [
            'items' => $videoparts,
        ]);

        return new Response($html, Response::HTTP_OK, ['Content-Type' => 'text/html']);
    }
}
