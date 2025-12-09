<?php

namespace App\Media\Service;

use App\Media\Entity\Sound;
use App\Media\Repository\SoundRepository;
use Symfony\Component\HttpFoundation\File\UploadedFile;

class SoundService
{
    private const UPLOAD_DIR = '/videodata/media/sounds';

    public function __construct(
        private readonly SoundRepository $repository,
    ) {
    }

    /**
     * Get all sounds ordered by name.
     *
     * @return Sound[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Get all boden sounds.
     *
     * @return Sound[]
     */
    public function getBoden(): array
    {
        return $this->repository->findBoden();
    }

    /**
     * Get all plane sounds.
     *
     * @return Sound[]
     */
    public function getPlane(): array
    {
        return $this->repository->findPlane();
    }

    /**
     * Get all freefall sounds.
     *
     * @return Sound[]
     */
    public function getFreefall(): array
    {
        return $this->repository->findFreefall();
    }

    /**
     * Get all canopy sounds.
     *
     * @return Sound[]
     */
    public function getCanopy(): array
    {
        return $this->repository->findCanopy();
    }

    /**
     * Get sounds by type.
     *
     * @return Sound[]
     */
    public function getByType(?string $type): array
    {
        return $this->repository->findByType($type);
    }

    /**
     * Find a sound by ID.
     */
    public function find(int $id): ?Sound
    {
        return $this->repository->findById($id);
    }

    /**
     * Create a new sound.
     */
    public function create(string $name, string $type, ?string $description = null, string $filePath = ''): Sound
    {
        $entity = new Sound();
        $entity->setName(trim($name));
        $entity->setType($type);
        $entity->setDescription($description ? trim($description) : null);
        $entity->setFilePath($filePath);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing sound.
     */
    public function update(Sound $entity, ?string $name = null, ?string $description = null): Sound
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
     * Delete a sound and its file.
     */
    public function delete(Sound $entity): bool
    {
        // Delete physical file
        if ($entity->getFilePath()) {
            $fullPath = self::UPLOAD_DIR . '/' . $entity->getFilePath();
            if (file_exists($fullPath)) {
                @unlink($fullPath);
            }
        }

        return $this->repository->deleteEntity($entity);
    }

    /**
     * Upload an MP3 or WAV file and create a sound entity.
     */
    public function uploadSound(UploadedFile $uploadedFile, string $type, ?string $name = null, ?string $description = null): Sound
    {
        // Validate type
        if (!in_array($type, [Sound::TYPE_BODEN, Sound::TYPE_PLANE, Sound::TYPE_FREEFALL, Sound::TYPE_CANOPY])) {
            throw new \InvalidArgumentException('Invalid type. Must be "boden", "plane", "freefall", or "canopy"');
        }

        // Validate file extension
        $extension = strtolower($uploadedFile->getClientOriginalExtension());
        if (!in_array($extension, ['mp3', 'wav'])) {
            throw new \InvalidArgumentException('Invalid file type. Only MP3 and WAV allowed');
        }

        // Validate mime type
        $allowedMimeTypes = ['audio/mpeg', 'audio/mp3', 'audio/wav', 'audio/x-wav', 'audio/wave'];
        $mimeType = $uploadedFile->getMimeType();
        if (!in_array($mimeType, $allowedMimeTypes)) {
            throw new \InvalidArgumentException('Invalid audio file type');
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

        // Set file permissions to 0644
        chmod(self::UPLOAD_DIR . '/' . $filename, 0644);

        // Create entity (waveform and duration will be post-processed)
        $entity = new Sound();
        $entity->setName($name ? trim($name) : $originalName);
        $entity->setType($type);
        $entity->setDescription($description ? trim($description) : null);
        $entity->setFilePath($filename);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Get waveform binary data for a sound.
     */
    public function getWaveform(int $id): ?string
    {
        $entity = $this->repository->findById($id);
        return $entity?->getWaveform();
    }

    /**
     * Get the full file path for a sound.
     */
    public function getFullFilePath(Sound $entity): string
    {
        return self::UPLOAD_DIR . '/' . $entity->getFilePath();
    }
}
