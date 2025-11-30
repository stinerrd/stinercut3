<?php

namespace App\Controller;

use App\Models\TandemMaster;
use App\Models\Setting;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

class TandemMastersController extends AppController
{
    #[Route('/tandem-masters', name: 'app_tandem_masters')]
    public function index(): Response
    {
        $this->addJs('js/tandem-masters.js');

        // Inject avatar settings as JS variables
        $this->addJsVar('avatarMaxUploadSize', Setting::get('avatar.max_upload_size', 5242880));
        $this->addJsVar('avatarWidth', Setting::get('avatar.width', 150));
        $this->addJsVar('avatarHeight', Setting::get('avatar.height', 150));

        $tandemMasters = TandemMaster::all();

        return $this->render('tandem_masters/index.html.twig', [
            'tandemMasters' => $tandemMasters,
        ]);
    }
}
