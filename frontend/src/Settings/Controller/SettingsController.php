<?php

namespace App\Settings\Controller;

use App\Controller\AppController;
use App\Settings\Service\SettingService;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class SettingsController extends AppController
{
    public function __construct(
        private readonly SettingService $settingService,
    ) {
    }

    #[Route('/settings', name: 'app_settings')]
    public function index(): Response
    {
        $this->addJs('js/settings/settings.js');

        $settingsByCategory = $this->settingService->getAllGroupedByCategory();
        $categories = array_keys($settingsByCategory);

        return $this->render('@Settings/index.html.twig', [
            'settingsByCategory' => $settingsByCategory,
            'categories' => $categories,
        ]);
    }
}
