<?php

namespace App\Workload\Service;

use App\Workload\Entity\Workload;
use App\Workload\Repository\WorkloadRepository;
use Symfony\Component\Uid\Uuid;

class WorkloadService
{
    public function __construct(
        private readonly WorkloadRepository $repository,
        private readonly QrCodeService $qrCodeService,
    ) {
    }

    /**
     * Get all workloads.
     *
     * @return Workload[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Find a workload by ID.
     */
    public function find(int $id): ?Workload
    {
        return $this->repository->findById($id);
    }

    /**
     * Get paginated workloads with filters.
     *
     * @param int $page Page number (1-based)
     * @param int $perPage Items per page
     * @param array $filters Filter criteria
     * @return array{workloads: Workload[], currentPage: int, totalPages: int, total: int, perPage: int}
     */
    public function getPaginated(int $page = 1, int $perPage = 20, array $filters = []): array
    {
        return $this->repository->findPaginated($page, $perPage, $filters);
    }

    /**
     * Create a new workload.
     * Note: Status is always set to 'created' - it will be changed by backend processing.
     */
    public function create(
        int $clientId,
        string $type,
        ?int $videographerId = null,
        ?string $desiredDate = null,
        string $video = Workload::MEDIA_MAYBE,
        string $photo = Workload::MEDIA_MAYBE
    ): Workload {
        $entity = new Workload();
        $entity->setUuid(Uuid::v4()->toRfc4122());
        $entity->setClientId($clientId);
        $entity->setType($type);
        $entity->setVideographerId($videographerId);
        $entity->setStatus(Workload::STATUS_CREATED);
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
            // Log error but allow workload creation to proceed
            error_log("ERROR: QR code generation failed for workload {$entity->getUuid()}: {$e->getMessage()}");
            error_log("ERROR: Stack trace: " . $e->getTraceAsString());
            $entity->setQr(null);
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing workload.
     */
    public function update(
        Workload $entity,
        ?int $clientId = null,
        ?string $type = null,
        ?int $videographerId = null,
        ?string $desiredDate = null,
        ?string $status = null,
        ?string $video = null,
        ?string $photo = null
    ): Workload {
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
     * Delete a workload.
     */
    public function delete(Workload $entity): bool
    {
        return $this->repository->deleteEntity($entity);
    }
}
