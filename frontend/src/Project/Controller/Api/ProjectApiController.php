<?php

namespace App\Project\Controller\Api;

use App\Project\Entity\Project;
use App\Project\Service\ProjectService;
use App\Videographer\Service\VideographerService;
use App\Client\Service\ClientService;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

#[Route('/api/projects')]
class ProjectApiController extends AbstractController
{
    public function __construct(
        private readonly ProjectService $projectService,
        private readonly VideographerService $videographerService,
        private readonly ClientService $clientService,
    ) {
    }

    /**
     * List projects with pagination and filters.
     * Returns HTML for AJAX or JSON based on Accept header.
     */
    #[Route('', name: 'api_projects_list', methods: ['POST'])]
    public function list(Request $request): Response
    {
        $data = json_decode($request->getContent(), true) ?? [];

        $page = (int) ($data['page'] ?? 1);
        $perPage = (int) ($data['per_page'] ?? 20);

        // Build filters
        $filters = [];
        if (!empty($data['date'])) {
            $filters['date'] = $data['date'];
        }
        if (!empty($data['status'])) {
            $filters['status'] = $data['status'];
        }
        if (!empty($data['videographer_id'])) {
            $filters['videographer_id'] = (int) $data['videographer_id'];
        }
        if (!empty($data['video'])) {
            $filters['video'] = $data['video'];
        }
        if (!empty($data['photo'])) {
            $filters['photo'] = $data['photo'];
        }
        if (!empty($data['type'])) {
            $filters['type'] = $data['type'];
        }
        if (!empty($data['client_id'])) {
            $filters['client_id'] = (int) $data['client_id'];
        }

        $result = $this->projectService->getPaginated($page, $perPage, $filters);

        // Check Accept header for response format
        $acceptHeader = $request->headers->get('Accept', '');
        $wantsJson = str_contains($acceptHeader, 'application/json');

        if ($wantsJson) {
            return new JsonResponse([
                'success' => true,
                'data' => [
                    'projects' => array_map(fn($p) => $p->toArray(), $result['projects']),
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
        return $this->render('@Project/_table.html.twig', [
            'projects' => $result['projects'],
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
     * Get a single project.
     */
    #[Route('/{id}', name: 'api_projects_show', methods: ['GET'])]
    public function show(int $id): JsonResponse
    {
        $project = $this->projectService->find($id);

        if (!$project) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Project not found',
            ], Response::HTTP_NOT_FOUND);
        }

        return new JsonResponse([
            'success' => true,
            'data' => $project->toArray(),
        ]);
    }

    /**
     * Create a new project.
     */
    #[Route('/create', name: 'api_projects_create', methods: ['POST'])]
    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true);

        // Validate required fields
        if (!isset($data['client_id']) || empty($data['client_id'])) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Client is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        if (!isset($data['type']) || empty(trim($data['type']))) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Type is required',
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate type
        if (!in_array($data['type'], Project::TYPES)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid type value. Allowed: ' . implode(', ', Project::TYPES),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate video enum
        if (isset($data['video']) && !in_array($data['video'], Project::MEDIA_OPTIONS)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid video value. Allowed: ' . implode(', ', Project::MEDIA_OPTIONS),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate photo enum
        if (isset($data['photo']) && !in_array($data['photo'], Project::MEDIA_OPTIONS)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid photo value. Allowed: ' . implode(', ', Project::MEDIA_OPTIONS),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate client exists
        $client = $this->clientService->find((int) $data['client_id']);
        if (!$client) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Client not found',
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate videographer exists if provided
        if (!empty($data['videographer_id'])) {
            $videographer = $this->videographerService->find((int) $data['videographer_id']);
            if (!$videographer) {
                return new JsonResponse([
                    'success' => false,
                    'error' => 'Videographer not found',
                ], Response::HTTP_BAD_REQUEST);
            }
        }

        $project = $this->projectService->create(
            clientId: (int) $data['client_id'],
            type: $data['type'],
            videographerId: !empty($data['videographer_id']) ? (int) $data['videographer_id'] : null,
            desiredDate: $data['desired_date'] ?? null,
            video: $data['video'] ?? Project::MEDIA_MAYBE,
            photo: $data['photo'] ?? Project::MEDIA_MAYBE,
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Project created',
            'data' => $project->toArray(),
        ], Response::HTTP_CREATED);
    }

    /**
     * Update an existing project.
     */
    #[Route('/{id}', name: 'api_projects_update', methods: ['PUT'])]
    public function update(int $id, Request $request): JsonResponse
    {
        $project = $this->projectService->find($id);

        if (!$project) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Project not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $data = json_decode($request->getContent(), true);

        // Validate type if provided
        if (isset($data['type']) && !in_array($data['type'], Project::TYPES)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid type value. Allowed: ' . implode(', ', Project::TYPES),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate video enum if provided
        if (isset($data['video']) && !in_array($data['video'], Project::MEDIA_OPTIONS)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid video value. Allowed: ' . implode(', ', Project::MEDIA_OPTIONS),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate photo enum if provided
        if (isset($data['photo']) && !in_array($data['photo'], Project::MEDIA_OPTIONS)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid photo value. Allowed: ' . implode(', ', Project::MEDIA_OPTIONS),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate status if provided
        if (isset($data['status']) && !in_array($data['status'], Project::STATUSES)) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Invalid status value. Allowed: ' . implode(', ', Project::STATUSES),
            ], Response::HTTP_BAD_REQUEST);
        }

        // Validate client exists if provided
        if (isset($data['client_id']) && !empty($data['client_id'])) {
            $client = $this->clientService->find((int) $data['client_id']);
            if (!$client) {
                return new JsonResponse([
                    'success' => false,
                    'error' => 'Client not found',
                ], Response::HTTP_BAD_REQUEST);
            }
        }

        // Validate videographer exists if provided
        if (isset($data['videographer_id']) && !empty($data['videographer_id'])) {
            $videographer = $this->videographerService->find((int) $data['videographer_id']);
            if (!$videographer) {
                return new JsonResponse([
                    'success' => false,
                    'error' => 'Videographer not found',
                ], Response::HTTP_BAD_REQUEST);
            }
        }

        $project = $this->projectService->update(
            entity: $project,
            clientId: array_key_exists('client_id', $data) ? ($data['client_id'] ? (int) $data['client_id'] : 0) : null,
            type: $data['type'] ?? null,
            videographerId: array_key_exists('videographer_id', $data) ? ($data['videographer_id'] ? (int) $data['videographer_id'] : 0) : null,
            desiredDate: $data['desired_date'] ?? null,
            status: $data['status'] ?? null,
            video: $data['video'] ?? null,
            photo: $data['photo'] ?? null,
        );

        return new JsonResponse([
            'success' => true,
            'message' => 'Project updated',
            'data' => $project->toArray(),
        ]);
    }

    /**
     * Delete a project.
     */
    #[Route('/{id}', name: 'api_projects_delete', methods: ['DELETE'])]
    public function delete(int $id): JsonResponse
    {
        $project = $this->projectService->find($id);

        if (!$project) {
            return new JsonResponse([
                'success' => false,
                'error' => 'Project not found',
            ], Response::HTTP_NOT_FOUND);
        }

        $this->projectService->delete($project);

        return new JsonResponse([
            'success' => true,
            'message' => 'Project deleted',
        ]);
    }
}
