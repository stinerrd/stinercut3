<?php

namespace App\Project\Controller;

use App\Controller\AppController;
use App\Project\Entity\Project;
use App\Project\Service\ProjectService;
use App\Videographer\Service\VideographerService;
use App\Client\Service\ClientService;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class ProjectController extends AppController
{
    public function __construct(
        private readonly ProjectService $projectService,
        private readonly VideographerService $videographerService,
        private readonly ClientService $clientService,
    ) {
        parent::__construct();
    }

    #[Route('/projects', name: 'app_projects')]
    public function index(Request $request): Response
    {
        // Add JavaScript files
        $this->addJs('js/ajax-content-loader.js');
        $this->addJs('js/project.js');

        // Get initial page with today's date filter
        $page = $request->query->getInt('page', 1);
        $filters = [
            'date' => $request->query->get('date', date('Y-m-d')),
        ];

        // Add other filters if present in query
        if ($request->query->has('status')) {
            $filters['status'] = $request->query->get('status');
        }
        if ($request->query->has('videographer_id')) {
            $filters['videographer_id'] = $request->query->getInt('videographer_id');
        }
        if ($request->query->has('client_id')) {
            $filters['client_id'] = $request->query->getInt('client_id');
        }
        if ($request->query->has('video')) {
            $filters['video'] = $request->query->get('video');
        }
        if ($request->query->has('photo')) {
            $filters['photo'] = $request->query->get('photo');
        }
        if ($request->query->has('type')) {
            $filters['type'] = $request->query->get('type');
        }

        $result = $this->projectService->getPaginated($page, 20, $filters);
        $videographers = $this->videographerService->getActive();
        $clients = $this->clientService->getAll();

        return $this->render('@Project/index.html.twig', [
            'projects' => $result['projects'],
            'pagination' => [
                'currentPage' => $result['currentPage'],
                'totalPages' => $result['totalPages'],
                'total' => $result['total'],
                'perPage' => $result['perPage'],
            ],
            'videographers' => $videographers,
            'clients' => $clients,
            'statuses' => Project::STATUSES,
            'mediaOptions' => Project::MEDIA_OPTIONS,
            'types' => Project::TYPES,
            'typeLabels' => Project::TYPE_LABELS,
            'filters' => $filters,
        ]);
    }
}
