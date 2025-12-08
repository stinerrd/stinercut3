<?php

declare(strict_types=1);

namespace App\Client\Controller\Api;

use App\Client\Service\ClientService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/clients')]
class ClientApiController extends AbstractController
{
    public function __construct(
        private readonly ClientService $clientService,
    ) {
    }

    /**
     * List clients with pagination and filters.
     * Returns HTML for AJAX or JSON based on Accept header.
     */
    #[Route('', name: 'api_clients_list', methods: ['POST'])]
    public function list(Request $request): Response
    {
        $data = json_decode($request->getContent(), true) ?? [];

        $page = (int) ($data['page'] ?? 1);
        $perPage = (int) ($data['per_page'] ?? 20);

        // Build filters
        $filters = [];
        if (!empty($data['name'])) {
            $filters['name'] = $data['name'];
        }
        if (isset($data['marketing_flag']) && $data['marketing_flag'] !== '') {
            $filters['marketing_flag'] = $data['marketing_flag'];
        }

        $result = $this->clientService->getPaginated($page, $perPage, $filters);

        // Check Accept header for response format
        $acceptHeader = $request->headers->get('Accept', '');
        $wantsJson = str_contains($acceptHeader, 'application/json');

        if ($wantsJson) {
            return new JsonResponse([
                'success' => true,
                'data' => [
                    'clients' => array_map(fn($c) => $c->toArray(), $result['clients']),
                    'pagination' => [
                        'currentPage' => $result['currentPage'],
                        'totalPages' => $result['totalPages'],
                        'total' => $result['total'],
                        'perPage' => $result['perPage'],
                    ],
                ],
            ]);
        }

        // Return HTML for AJAX
        return $this->render('@Client/_table.html.twig', [
            'clients' => $result['clients'],
            'pagination' => [
                'currentPage' => $result['currentPage'],
                'totalPages' => $result['totalPages'],
                'total' => $result['total'],
                'perPage' => $result['perPage'],
            ],
            'filters' => $filters,
        ]);
    }

    /**
     * Get a single client.
     */
    #[Route('/{id}', name: 'api_clients_show', methods: ['GET'])]
    public function show(int $id): JsonResponse
    {
        $client = $this->clientService->find($id);

        if (!$client) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Client not found',
            ], Response::HTTP_NOT_FOUND);
        }

        return new JsonResponse([
            'success' => true,
            'data' => $client->toArray(),
        ]);
    }

    /**
     * Create a new client.
     */
    #[Route('/create', name: 'api_clients_create', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        // Validate required fields
        if (!isset($data['name']) || empty(trim($data['name']))) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Name is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        $client = $this->clientService->create(
            name: $data['name'],
            email: $data['email'] ?? null,
            phone: $data['phone'] ?? null,
            marketingFlag: (bool) ($data['marketing_flag'] ?? false),
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Client created',
            'data' => $client->toArray(),
        ], Response::HTTP_CREATED);
    }

    /**
     * Update an existing client.
     */
    #[Route('/{id}', name: 'api_clients_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $client = $this->clientService->find($id);

        if (!$client) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Client not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        $client = $this->clientService->update(
            entity: $client,
            name: $data['name'] ?? null,
            email: array_key_exists('email', $data) ? $data['email'] : null,
            phone: array_key_exists('phone', $data) ? $data['phone'] : null,
            marketingFlag: isset($data['marketing_flag']) ? (bool) $data['marketing_flag'] : null,
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Client updated',
            'data' => $client->toArray(),
        ]);
    }

    /**
     * Delete a client.
     */
    #[Route('/{id}', name: 'api_clients_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $client = $this->clientService->find($id);

        if (!$client) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Client not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->clientService->delete($client);

        return new JsonResponse([
            'success' => true,
            'message' => 'Client deleted',
        ]);
    }
}
