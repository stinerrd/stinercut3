<?php

namespace App\Splashscreen\Service;

use App\Splashscreen\Entity\Splashscreen;
use App\Splashscreen\Repository\SplashscreenRepository;
use App\Service\SvgParserService;
use Symfony\Component\HttpFoundation\File\UploadedFile;
use Symfony\Contracts\HttpClient\HttpClientInterface;

class SplashscreenService
{
    public function __construct(
        private readonly SplashscreenRepository $repository,
        private readonly SvgParserService $svgParserService,
        private readonly HttpClientInterface $httpClient,
    ) {
    }

    /**
     * Get all splashscreens ordered by name.
     *
     * @return Splashscreen[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Get all image splashscreens ordered by name.
     *
     * @return Splashscreen[]
     */
    public function getImages(): array
    {
        return $this->repository->findImages();
    }

    /**
     * Get all font splashscreens ordered by name.
     *
     * @return Splashscreen[]
     */
    public function getFonts(): array
    {
        return $this->repository->findFonts();
    }

    /**
     * Get splashscreens by category.
     *
     * @return Splashscreen[]
     */
    public function getByCategory(?string $category): array
    {
        return $this->repository->findByCategory($category);
    }

    /**
     * Find a splashscreen by ID.
     */
    public function find(int $id): ?Splashscreen
    {
        return $this->repository->findById($id);
    }

    /**
     * Create a new splashscreen.
     */
    public function create(string $name, string $category, string $svgContent): Splashscreen
    {
        $entity = new Splashscreen();
        $entity->setName(trim($name));
        $entity->setCategory($category);
        $entity->setSvgContent($this->svgParserService->sanitize($svgContent));

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing splashscreen.
     */
    public function update(Splashscreen $entity, ?string $name = null, ?string $svgContent = null): Splashscreen
    {
        if ($name !== null) {
            $entity->setName(trim($name));
        }

        if ($svgContent !== null) {
            $entity->setSvgContent($this->svgParserService->sanitize($svgContent));
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Delete a splashscreen.
     */
    public function delete(Splashscreen $entity): bool
    {
        return $this->repository->deleteEntity($entity);
    }

    /**
     * Import an SVG file and create both image and font records.
     *
     * @return array{image: Splashscreen, font: Splashscreen}
     */
    public function importSvg(string $svgContent, string $baseName): array
    {
        $parsed = $this->svgParserService->parseForImport($svgContent, $baseName);

        $image = new Splashscreen();
        $image->setName($parsed['image']['name']);
        $image->setCategory($parsed['image']['category']);
        $image->setSvgContent($parsed['image']['svg_content']);
        $image = $this->repository->saveEntity($image);

        $font = new Splashscreen();
        $font->setName($parsed['font']['name']);
        $font->setCategory($parsed['font']['category']);
        $font->setSvgContent($parsed['font']['svg_content']);
        $font = $this->repository->saveEntity($font);

        return [
            'image' => $image,
            'font' => $font,
        ];
    }

    /**
     * Import a TTF/OTF font file and create a font record.
     */
    public function importTtf(UploadedFile $uploadedFile): Splashscreen
    {
        $formData = new \Symfony\Component\Mime\Part\Multipart\FormDataPart([
            'file' => \Symfony\Component\Mime\Part\DataPart::fromPath(
                $uploadedFile->getRealPath(),
                $uploadedFile->getClientOriginalName(),
                $uploadedFile->getMimeType()
            ),
        ]);

        $response = $this->httpClient->request('POST', 'http://backend:8000/api/fonts/convert', [
            'headers' => $formData->getPreparedHeaders()->toArray(),
            'body' => $formData->bodyToIterable(),
        ]);

        $result = $response->toArray();

        if (!($result['success'] ?? false)) {
            throw new \RuntimeException($result['detail'] ?? 'Font conversion failed');
        }

        $entity = new Splashscreen();
        $entity->setName($result['font_name']);
        $entity->setCategory('font');
        $entity->setSvgContent($result['svg_paths']);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Get SVG content for display, with appropriate transformations.
     */
    public function getSvgForDisplay(Splashscreen $entity, ?int $fontId = null): string
    {
        $svgContent = $entity->getSvgContent();

        if ($entity->isFont()) {
            return $this->svgParserService->generateFontPreview($svgContent, $fontId ?? $entity->getId());
        }

        return $this->svgParserService->replaceDimensionPlaceholders($svgContent);
    }

    /**
     * Generate font preview SVG from raw content.
     */
    public function generateFontPreview(string $fontContent): string
    {
        if (empty(trim($fontContent))) {
            return '<?xml version="1.0"?><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 50"><text x="10" y="30" fill="#666">No content</text></svg>';
        }

        return $this->svgParserService->generateFontPreview($fontContent);
    }
}
