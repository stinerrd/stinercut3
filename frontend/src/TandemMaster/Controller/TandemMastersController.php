<?php

namespace App\TandemMaster\Controller;

use App\Controller\AppController;
use App\TandemMaster\Service\TandemMasterService;
use App\Settings\Repository\SettingRepository;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class TandemMastersController extends AppController
{
    public function __construct(
        private readonly TandemMasterService $tandemMasterService,
    ) {
    }

    #[Route('/tandem-masters', name: 'app_tandem_masters')]
    public function index(): Response
    {
        $this->addJs('js/tandem-masters.js');

        // Inject avatar settings as JS variables
        $this->addJsVar('avatarMaxUploadSize', SettingRepository::get('avatar.max_upload_size', 5242880));
        $this->addJsVar('avatarWidth', SettingRepository::get('avatar.width', 150));
        $this->addJsVar('avatarHeight', SettingRepository::get('avatar.height', 150));

        $tandemMasters = $this->tandemMasterService->getAll();

        return $this->render('@TandemMaster/index.html.twig', [
            'tandemMasters' => $tandemMasters,
        ]);
    }
}
