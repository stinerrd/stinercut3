<?php

namespace App\Controller;

use App\Service\SettingsService;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class SettingsController extends AppController
{
    public function __construct(
        private readonly SettingsService $settingsService,
    ) {
    }

    #[Route('/settings', name: 'app_settings')]
    public function index(): Response
    {
        $this->addJs('js/settings/settings.js');

        $settingsByCategory = $this->settingsService->getAllGroupedByCategory();
        $categories = array_keys($settingsByCategory);

        return $this->render('settings/index.html.twig', [
            'settingsByCategory' => $settingsByCategory,
            'categories' => $categories,
        ]);
    }
}
