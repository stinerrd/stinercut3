<?php

namespace App\Controller\Api;

use App\Service\SettingsService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/settings')]
class SettingsApiController extends AbstractController
{
    public function __construct(
        private readonly SettingsService $settingsService,
    ) {
    }

    /**
     * List all settings.
     */
    #[Route('', name: 'api_settings_list', methods: ['GET'])]
    public function list(): JsonResponse
    {
        $settings = $this->settingsService->getAll();

        return new JsonResponse([
            'success' => true,
            'data' => $settings->toArray(),
        ]);
    }

    /**
     * Get a single setting by key.
     */
    #[Route('/{key}', name: 'api_settings_get', methods: ['GET'], requirements: ['key' => '.+'])]
    public function get(string $key): JsonResponse
    {
        $setting = $this->settingsService->getByKey($key);

        if (!$setting) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Setting not found',
            ], Response::HTTP_NOT_FOUND);
        }

        return new JsonResponse([
            'success' => true,
            'data' => $setting->toArray(),
        ]);
    }

    /**
     * Update a single setting by key.
     */
    #[Route('/{key}', name: 'api_settings_update', methods: ['PUT'], requirements: ['key' => '.+'])]
    public function update(string $key, Request $request): JsonResponse
    {
        $setting = $this->settingsService->getByKey($key);

        if (!$setting) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Setting not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        if (!isset($data['value'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Missing value field',
            ], Response::HTTP_BAD_REQUEST);
        }

        $this->settingsService->setValue($key, $data['value']);

        // Reload to get updated data
        $setting = $this->settingsService->getByKey($key);

        return new JsonResponse([
            'success' => true,
            'message' => 'Setting updated',
            'data' => $setting->toArray(),
        ]);
    }

    /**
     * Update multiple settings at once.
     */
    #[Route('/batch', name: 'api_settings_batch_update', methods: ['PUT'], priority: 10)]
    public function batchUpdate(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        if (!isset($data['settings']) || !is_array($data['settings'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Missing or invalid settings field',
            ], Response::HTTP_BAD_REQUEST);
        }

        $result = $this->settingsService->setValues($data['settings']);

        return new JsonResponse([
            'success' => count($result['errors']) === 0,
            'message' => count($result['updated']) . ' setting(s) updated',
            'updated' => $result['updated'],
            'errors' => $result['errors'],
        ]);
    }
}
