<?php

namespace App\Videographer\Controller;

use App\Controller\AppController;
use App\Videographer\Service\VideographerService;
use App\Settings\Repository\SettingRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class VideographersController extends AppController
{
    public function __construct(
        private readonly VideographerService $videographerService,
    ) {
    }

    #[Route('/videographers', name: 'app_videographers')]
    public function index(): Response
    {
        $this->addJs('js/videographers.js');

        // Inject avatar settings as JS variables
        $this->addJsVar('avatarMaxUploadSize', SettingRepository::get('avatar.max_upload_size', 5242880));
        $this->addJsVar('avatarWidth', SettingRepository::get('avatar.width', 150));
        $this->addJsVar('avatarHeight', SettingRepository::get('avatar.height', 150));

        $videographers = $this->videographerService->getAll();

        return $this->render('@Videographer/index.html.twig', [
            'videographers' => $videographers,
        ]);
    }
}
