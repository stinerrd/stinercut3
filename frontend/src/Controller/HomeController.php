<?php

namespace App\Controller;

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class HomeController extends AppController
{
    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        $this->addJs('js/detector-status.js');

        return $this->render('home/index.html.twig');
    }
}
