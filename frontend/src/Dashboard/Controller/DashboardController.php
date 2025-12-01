<?php

namespace App\Dashboard\Controller;

use App\Controller\AppController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class DashboardController extends AppController
{
    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        $this->addJs('js/detector-status.js');

        return $this->render('@Dashboard/index.html.twig');
    }
}
