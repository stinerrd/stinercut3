<?php

namespace App\Splashscreen\Controller;

use App\Controller\AppController;
use App\Splashscreen\Service\SplashscreenService;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class SplashscreensController extends AppController
{
    public function __construct(
        private readonly SplashscreenService $splashscreenService,
    ) {
        parent::__construct();
    }

    #[Route('/splashscreens', name: 'app_splashscreens')]
    public function index(): Response
    {
        $this->addJs('js/lazy-tabs.js');
        $this->addJs('js/splashscreens.js');

        $images = $this->splashscreenService->getImages();

        return $this->render('@Splashscreen/index.html.twig', [
            'images' => $images,
        ]);
    }
}
