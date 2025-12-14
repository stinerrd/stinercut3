<?php

namespace App\Project\Service;

use Endroid\QrCode\Builder\Builder;
use Endroid\QrCode\Encoding\Encoding;
use Endroid\QrCode\ErrorCorrectionLevel;
use Endroid\QrCode\RoundBlockSizeMode;
use Endroid\QrCode\Writer\PngWriter;

class QrCodeService
{
    /**
     * Generate QR code PNG image for a given workload UUID.
     *
     * @param string $uuid Workload UUID
     * @return string PNG image binary data
     */
    public function generateQrCode(string $uuid): string
    {
        $text = "Stinercut: {$uuid}";

        $result = Builder::create()
            ->writer(new PngWriter())
            ->data($text)
            ->encoding(new Encoding('UTF-8'))
            ->errorCorrectionLevel(ErrorCorrectionLevel::Medium)
            ->size(300)
            ->margin(10)
            ->roundBlockSizeMode(RoundBlockSizeMode::Margin)
            ->build();

        return $result->getString();
    }
}
