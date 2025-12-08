<?php

namespace App\Workload\Controller;

use App\Controller\AppController;
use App\Workload\Entity\Workload;
use App\Workload\Service\WorkloadService;
use App\Videographer\Service\VideographerService;
use App\Client\Service\ClientService;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class WorkloadController extends AppController
{
    public function __construct(
        private readonly WorkloadService $workloadService,
        private readonly VideographerService $videographerService,
        private readonly ClientService $clientService,
    ) {
        parent::__construct();
    }

    #[Route('/workloads', name: 'app_workloads')]
    public function index(Request $request): Response
    {
        // Add JavaScript files
        $this->addJs('js/ajax-content-loader.js');
        $this->addJs('js/workload.js');

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

        $result = $this->workloadService->getPaginated($page, 20, $filters);
        $videographers = $this->videographerService->getActive();
        $clients = $this->clientService->getAll();

        return $this->render('@Workload/index.html.twig', [
            'workloads' => $result['workloads'],
            'pagination' => [
                'currentPage' => $result['currentPage'],
                'totalPages' => $result['totalPages'],
                'total' => $result['total'],
                'perPage' => $result['perPage'],
            ],
            'videographers' => $videographers,
            'clients' => $clients,
            'statuses' => Workload::STATUSES,
            'mediaOptions' => Workload::MEDIA_OPTIONS,
            'types' => Workload::TYPES,
            'typeLabels' => Workload::TYPE_LABELS,
            'filters' => $filters,
        ]);
    }
}
