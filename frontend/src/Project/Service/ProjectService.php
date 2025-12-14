<?php

namespace App\Project\Service;

use App\Project\Entity\Project;
use App\Project\Repository\ProjectRepository;
use Symfony\Component\Uid\Uuid;

class ProjectService
{
    public function __construct(
        private readonly ProjectRepository $repository,
        private readonly QrCodeService $qrCodeService,
    ) {
    }

    /**
     * Get all projects.
     *
     * @return Project[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Find a project by ID.
     */
    public function find(int $id): ?Project
    {
        return $this->repository->findById($id);
    }

    /**
     * Get paginated projects with filters.
     *
     * @param int $page Page number (1-based)
     * @param int $perPage Items per page
     * @param array $filters Filter criteria
     * @return array{projects: Project[], currentPage: int, totalPages: int, total: int, perPage: int}
     */
    public function getPaginated(int $page = 1, int $perPage = 20, array $filters = []): array
    {
        return $this->repository->findPaginated($page, $perPage, $filters);
    }

    /**
     * Create a new project.
     * Note: Status is always set to 'created' - it will be changed by backend processing.
     */
    public function create(
        int $clientId,
        string $type,
        ?int $videographerId = null,
        ?string $desiredDate = null,
        string $video = Project::MEDIA_MAYBE,
        string $photo = Project::MEDIA_MAYBE
    ): Project {
        $entity = new Project();
        $entity->setUuid(Uuid::v4()->toRfc4122());
        $entity->setClientId($clientId);
        $entity->setType($type);
        $entity->setVideographerId($videographerId);
        $entity->setStatus(Project::STATUS_CREATED);
        $entity->setVideo($video);
        $entity->setPhoto($photo);

        if ($desiredDate) {
            $entity->setDesiredDate(new \DateTime($desiredDate));
        } else {
            $entity->setDesiredDate(new \DateTime('today'));
        }

        // Generate QR code
        try {
            error_log("DEBUG: Attempting QR generation for UUID: {$entity->getUuid()}");
            $qrCode = $this->qrCodeService->generateQrCode($entity->getUuid());
            error_log("DEBUG: QR generated successfully, size: " . strlen($qrCode) . " bytes");
            $entity->setQr($qrCode);
            error_log("DEBUG: QR set on entity");
        } catch (\Exception $e) {
            // Log error but allow project creation to proceed
            error_log("ERROR: QR code generation failed for project {$entity->getUuid()}: {$e->getMessage()}");
            error_log("ERROR: Stack trace: " . $e->getTraceAsString());
            $entity->setQr(null);
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing project.
     */
    public function update(
        Project $entity,
        ?int $clientId = null,
        ?string $type = null,
        ?int $videographerId = null,
        ?string $desiredDate = null,
        ?string $status = null,
        ?string $video = null,
        ?string $photo = null
    ): Project {
        if ($clientId !== null) {
            $entity->setClientId($clientId ?: null);
        }

        if ($type !== null) {
            $entity->setType($type);
        }

        if ($videographerId !== null) {
            $entity->setVideographerId($videographerId ?: null);
        }

        if ($desiredDate !== null) {
            $entity->setDesiredDate(new \DateTime($desiredDate));
        }

        if ($status !== null) {
            $entity->setStatus($status);
        }

        if ($video !== null) {
            $entity->setVideo($video);
        }

        if ($photo !== null) {
            $entity->setPhoto($photo);
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Delete a project.
     */
    public function delete(Project $entity): bool
    {
        return $this->repository->deleteEntity($entity);
    }
}
