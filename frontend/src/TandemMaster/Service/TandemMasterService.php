<?php

namespace App\TandemMaster\Service;

use App\TandemMaster\Entity\TandemMaster;
use App\TandemMaster\Repository\TandemMasterRepository;
use App\Settings\Repository\SettingRepository;
use Symfony\Component\HttpFoundation\File\UploadedFile;

class TandemMasterService
{
    public function __construct(
        private readonly TandemMasterRepository $repository,
    ) {
    }

    /**
     * Get all tandem masters.
     *
     * @return TandemMaster[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Get all active tandem masters.
     *
     * @return TandemMaster[]
     */
    public function getActive(): array
    {
        return $this->repository->findActive();
    }

    /**
     * Find a tandem master by ID.
     */
    public function find(int $id): ?TandemMaster
    {
        return $this->repository->findById($id);
    }

    /**
     * Create a new tandem master.
     */
    public function create(string $name, bool $active = true): TandemMaster
    {
        $entity = new TandemMaster();
        $entity->setName(trim($name));
        $entity->setActive($active);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing tandem master.
     */
    public function update(TandemMaster $entity, ?string $name = null, ?bool $active = null): TandemMaster
    {
        if ($name !== null) {
            $entity->setName(trim($name));
        }

        if ($active !== null) {
            $entity->setActive($active);
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Delete a tandem master.
     */
    public function delete(TandemMaster $entity): bool
    {
        return $this->repository->deleteEntity($entity);
    }

    /**
     * Get image data for a tandem master.
     */
    public function getImageData(int $id): ?array
    {
        return $this->repository->getImageData($id);
    }

    /**
     * Upload and process avatar image.
     *
     * @throws \Exception
     */
    public function uploadImage(TandemMaster $entity, UploadedFile $uploadedFile): TandemMaster
    {
        // Validate file size
        $maxSize = SettingRepository::get('avatar.max_upload_size', 5242880);
        if ($uploadedFile->getSize() > $maxSize) {
            throw new \InvalidArgumentException(
                'File size exceeds maximum allowed (' . ($maxSize / 1024 / 1024) . 'MB)'
            );
        }

        // Validate MIME type
        $allowedMimes = ['image/jpeg', 'image/png', 'image/gif'];
        $fileMime = $uploadedFile->getMimeType();
        if (!in_array($fileMime, $allowedMimes)) {
            throw new \InvalidArgumentException('Invalid file type. Allowed: JPEG, PNG, GIF');
        }

        // Read image file
        $imageData = file_get_contents($uploadedFile->getRealPath());

        // Load image resource
        $image = imagecreatefromstring($imageData);
        if (!$image) {
            throw new \RuntimeException('Failed to process image');
        }

        // Get target dimensions
        $targetWidth = SettingRepository::get('avatar.width', 150);
        $targetHeight = SettingRepository::get('avatar.height', 150);

        // Create resized image
        $resized = imagecreatetruecolor($targetWidth, $targetHeight);
        if (!$resized) {
            imagedestroy($image);
            throw new \RuntimeException('Failed to create image resource');
        }

        // Resize and copy
        imagecopyresampled(
            $resized,
            $image,
            0,
            0,
            0,
            0,
            $targetWidth,
            $targetHeight,
            imagesx($image),
            imagesy($image)
        );

        // Convert to JPEG
        ob_start();
        imagejpeg($resized, null, 90);
        $jpegData = ob_get_clean();

        // Clean up
        imagedestroy($image);
        imagedestroy($resized);

        // Update entity
        $entity->setImage($jpegData);
        $entity->setImageMime('image/jpeg');

        return $this->repository->saveEntity($entity);
    }
}
