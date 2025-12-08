<?php

declare(strict_types=1);

namespace App\Client\Controller;

use App\Controller\AppController;
use App\Client\Service\ClientService;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class ClientController extends AppController
{
    public function __construct(
        private readonly ClientService $clientService,
    ) {
        parent::__construct();
    }

    #[Route('/clients', name: 'app_clients')]
    public function index(Request $request): Response
    {
        // Add JavaScript files
        $this->addJs('js/ajax-content-loader.js');
        $this->addJs('js/clients.js');

        // Get initial page
        $page = $request->query->getInt('page', 1);
        $filters = [];

        // Add filters if present in query
        if ($request->query->has('name')) {
            $filters['name'] = $request->query->get('name');
        }
        if ($request->query->has('marketing_flag') && $request->query->get('marketing_flag') !== '') {
            $filters['marketing_flag'] = $request->query->get('marketing_flag');
        }

        $result = $this->clientService->getPaginated($page, 20, $filters);

        return $this->render('@Client/index.html.twig', [
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
}
