<?php

namespace App\Controller;

use App\Models\Splashscreen;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class SplashscreensController extends AppController
{
    #[Route('/splashscreens', name: 'app_splashscreens')]
    public function index(): Response
    {
        // Images tab is eager loaded, fonts tab is lazy loaded
        $images = Splashscreen::images()->orderBy('name')->get();

        return $this->render('splashscreens/index.html.twig', [
            'images' => $images,
        ]);
    }
}
