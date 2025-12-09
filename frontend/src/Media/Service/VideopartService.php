<?php

namespace App\Media\Service;

use App\Media\Entity\Videopart;
use App\Media\Repository\VideopartRepository;
use Symfony\Component\HttpFoundation\File\UploadedFile;

class VideopartService
{
    private const UPLOAD_DIR = '/videodata/media/videoparts';

    public function __construct(
        private readonly VideopartRepository $repository,
    ) {
    }

    /**
     * Get all videoparts ordered by name.
     *
     * @return Videopart[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Get all intro videos.
     *
     * @return Videopart[]
     */
    public function getIntros(): array
    {
        return $this->repository->findIntros();
    }

    /**
     * Get all outro videos.
     *
     * @return Videopart[]
     */
    public function getOutros(): array
    {
        return $this->repository->findOutros();
    }

    /**
     * Get videoparts by type.
     *
     * @return Videopart[]
     */
    public function getByType(?string $type): array
    {
        return $this->repository->findByType($type);
    }

    /**
     * Find a videopart by ID.
     */
    public function find(int $id): ?Videopart
    {
        return $this->repository->findById($id);
    }

    /**
     * Create a new videopart.
     */
    public function create(string $name, string $type, ?string $description = null, string $filePath = ''): Videopart
    {
        $entity = new Videopart();
        $entity->setName(trim($name));
        $entity->setType($type);
        $entity->setDescription($description ? trim($description) : null);
        $entity->setFilePath($filePath);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing videopart.
     */
    public function update(Videopart $entity, ?string $name = null, ?string $description = null): Videopart
    {
        if ($name !== null) {
            $entity->setName(trim($name));
        }

        if ($description !== null) {
            $entity->setDescription(trim($description) ?: null);
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Delete a videopart, its file, and associated folder.
     */
    public function delete(Videopart $entity): bool
    {
        if ($entity->getFilePath()) {
            $fullPath = self::UPLOAD_DIR . '/' . $entity->getFilePath();

            // Delete physical video file
            if (file_exists($fullPath)) {
                @unlink($fullPath);
            }

            // Delete associated folder (for resolution variants)
            $folderPath = pathinfo($fullPath, PATHINFO_DIRNAME) . '/' . pathinfo($fullPath, PATHINFO_FILENAME);
            if (is_dir($folderPath)) {
                $this->deleteDirectory($folderPath);
            }
        }

        return $this->repository->deleteEntity($entity);
    }

    /**
     * Recursively delete a directory and its contents.
     */
    private function deleteDirectory(string $dir): bool
    {
        if (!is_dir($dir)) {
            return false;
        }

        $items = array_diff(scandir($dir), ['.', '..']);
        foreach ($items as $item) {
            $path = $dir . '/' . $item;
            if (is_dir($path)) {
                $this->deleteDirectory($path);
            } else {
                @unlink($path);
            }
        }

        return @rmdir($dir);
    }

    /**
     * Upload a video file and create a videopart entity.
     */
    public function uploadVideo(UploadedFile $uploadedFile, string $type, ?string $name = null, ?string $description = null): Videopart
    {
        // Validate type
        if (!in_array($type, [Videopart::TYPE_INTRO, Videopart::TYPE_OUTRO])) {
            throw new \InvalidArgumentException('Invalid type. Must be "intro" or "outro"');
        }

        // Validate file extension
        $extension = strtolower($uploadedFile->getClientOriginalExtension());
        if (!in_array($extension, ['mp4', 'mov'])) {
            throw new \InvalidArgumentException('Invalid file type. Allowed: MP4, MOV');
        }

        // Validate mime type
        $allowedMimeTypes = ['video/mp4', 'video/quicktime', 'video/x-m4v'];
        $mimeType = $uploadedFile->getMimeType();
        if (!in_array($mimeType, $allowedMimeTypes)) {
            throw new \InvalidArgumentException('Invalid video file type');
        }

        // Create directory if it doesn't exist
        if (!is_dir(self::UPLOAD_DIR)) {
            mkdir(self::UPLOAD_DIR, 0755, true);
        }

        // Generate unique filename
        $originalName = pathinfo($uploadedFile->getClientOriginalName(), PATHINFO_FILENAME);
        $filename = sprintf(
            '%s_%s_%s.%s',
            $type,
            date('Ymd_His'),
            substr(uniqid(), -6),
            $extension
        );

        // Move file
        $uploadedFile->move(self::UPLOAD_DIR, $filename);

        // Set file permissions
        chmod(self::UPLOAD_DIR . '/' . $filename, 0644);

        // Create entity
        $entity = new Videopart();
        $entity->setName($name ? trim($name) : $originalName);
        $entity->setType($type);
        $entity->setDescription($description ? trim($description) : null);
        $entity->setFilePath($filename);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Get thumbnail binary data for a videopart.
     */
    public function getThumbnail(int $id): ?string
    {
        $entity = $this->repository->findById($id);
        return $entity?->getThumbnail();
    }

    /**
     * Get the full file path for a videopart.
     */
    public function getFullFilePath(Videopart $entity): string
    {
        return self::UPLOAD_DIR . '/' . $entity->getFilePath();
    }
}
