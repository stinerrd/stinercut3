<?php

namespace App\Media\Controller\Api;

use App\Media\Service\SoundService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\BinaryFileResponse;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\ResponseHeaderBag;
use Symfony\Component\Routing\Attribute\Route;
use Twig\Environment;

#[Route('/api/sounds')]
class SoundsApiController extends AbstractController
{
    public function __construct(
        private readonly SoundService $soundService,
        private readonly Environment $twig,
    ) {
    }

    /**
     * List all sounds with optional type filter.
     */
    #[Route('', name: 'api_sounds_list', methods: ['GET'])]
    public function list(Request $request): JsonResponse
    {
        $type = $request->query->get('type');
        $sounds = $this->soundService->getByType($type);

        return new JsonResponse([
            'success' => true,
            'data' => array_map(fn($entity) => $entity->toArray(), $sounds),
        ]);
    }

    /**
     * Get a single sound.
     */
    #[Route('/{id}', name: 'api_sounds_get', methods: ['GET'], requirements: ['id' => '\d+'])]
    public function get(int $id): JsonResponse
    {
        $sound = $this->soundService->find($id);

        if (!$sound) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Sound not found',
            ], Response::HTTP_NOT_FOUND);
        }

        return new JsonResponse([
            'success' => true,
            'data' => $sound->toArray(),
        ]);
    }

    /**
     * Upload a new MP3 or WAV file.
     */
    #[Route('/upload', name: 'api_sounds_upload', methods: ['POST'])]
    public function upload(Request $request): JsonResponse
    {
        $uploadedFile = $request->files->get('audio');

        if (!$uploadedFile) {
            return new JsonResponse([
                'success' => false,
                'error' => 'No audio file provided',
            ], Response::HTTP_BAD_REQUEST);
        }

        $type = $request->request->get('type');
        if (!$type || !in_array($type, ['boden', 'plane', 'freefall', 'canopy'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Type must be "boden", "plane", "freefall", or "canopy"',
            ], Response::HTTP_BAD_REQUEST);
        }

        $name = $request->request->get('name');
        $description = $request->request->get('description');

        try {
            $sound = $this->soundService->uploadSound(
                $uploadedFile,
                $type,
                $name,
                $description
            );

            return new JsonResponse([
                'success' => true,
                'message' => 'Sound uploaded successfully',
                'data' => $sound->toArray(),
            ], Response::HTTP_CREATED);
        } catch (\InvalidArgumentException $e) {
            return new JsonResponse([
                'success' => false,
                'error' => $e->getMessage(),
            ], Response::HTTP_BAD_REQUEST);
        } catch (\Exception $e) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Failed to upload sound: ' . $e->getMessage(),
            ], Response::HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    /**
     * Update an existing sound.
     */
    #[Route('/{id}', name: 'api_sounds_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $sound = $this->soundService->find($id);

        if (!$sound) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Sound not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        $sound = $this->soundService->update(
            $sound,
            $data['name'] ?? null,
            $data['description'] ?? null
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Sound updated',
            'data' => $sound->toArray(),
        ]);
    }

    /**
     * Delete a sound.
     */
    #[Route('/{id}', name: 'api_sounds_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $sound = $this->soundService->find($id);

        if (!$sound) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Sound not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->soundService->delete($sound);

        return new JsonResponse([
            'success' => true,
            'message' => 'Sound deleted',
        ]);
    }

    /**
     * Get waveform image for a sound.
     */
    #[Route('/{id}/waveform', name: 'api_sounds_waveform', methods: ['GET'])]
    public function waveform(int $id): Response
    {
        $waveform = $this->soundService->getWaveform($id);

        if (!$waveform) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        return new Response(
            $waveform,
            Response::HTTP_OK,
            [
                'Content-Type' => 'image/png',
                'Cache-Control' => 'public, max-age=3600',
            ]
        );
    }

    /**
     * Stream audio file for preview playback.
     */
    #[Route('/{id}/audio', name: 'api_sounds_audio', methods: ['GET'])]
    public function audio(int $id): Response
    {
        $sound = $this->soundService->find($id);

        if (!$sound) {
            return new Response('', Response::HTTP_NOT_FOUND);
        }

        $filePath = $this->soundService->getFullFilePath($sound);

        if (!file_exists($filePath)) {
            return new Response('Audio file not found', Response::HTTP_NOT_FOUND);
        }

        $response = new BinaryFileResponse($filePath);
        $response->headers->set('Content-Type', 'audio/mpeg');
        $response->headers->set('Accept-Ranges', 'bytes');
        $response->headers->set('Cache-Control', 'public, max-age=3600');
        $response->setContentDisposition(ResponseHeaderBag::DISPOSITION_INLINE, $sound->getName() . '.mp3');

        return $response;
    }

    /**
     * Get HTML content for sounds tab (lazy loading).
     */
    #[Route('/tab/content', name: 'api_sounds_tab', methods: ['GET'])]
    public function tabContent(): Response
    {
        $sounds = $this->soundService->getAll();

        $html = $this->twig->render('@Media/_tab_sounds.html.twig', [
            'items' => $sounds,
        ]);

        return new Response($html, Response::HTTP_OK, ['Content-Type' => 'text/html']);
    }
}
