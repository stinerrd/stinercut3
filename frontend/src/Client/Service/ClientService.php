<?php

declare(strict_types=1);

namespace App\Client\Service;

use App\Client\Entity\Client;
use App\Client\Repository\ClientRepository;

class ClientService
{
    public function __construct(
        private readonly ClientRepository $repository,
    ) {
    }

    /**
     * Get all clients.
     *
     * @return Client[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Find a client by ID.
     */
    public function find(int $id): ?Client
    {
        return $this->repository->findById($id);
    }

    /**
     * Get paginated clients with filters.
     *
     * @param int $page Page number (1-based)
     * @param int $perPage Items per page
     * @param array $filters Filter criteria
     * @return array{clients: Client[], currentPage: int, totalPages: int, total: int, perPage: int}
     */
    public function getPaginated(int $page = 1, int $perPage = 20, array $filters = []): array
    {
        return $this->repository->findPaginated($page, $perPage, $filters);
    }

    /**
     * Create a new client.
     */
    public function create(
        string $name,
        ?string $email = null,
        ?string $phone = null,
        bool $marketingFlag = false
    ): Client {
        $entity = new Client();
        $entity->setName(trim($name));
        $entity->setEmail($email ? trim($email) : null);
        $entity->setPhone($phone ? trim($phone) : null);
        $entity->setMarketingFlag($marketingFlag);

        return $this->repository->saveEntity($entity);
    }

    /**
     * Update an existing client.
     */
    public function update(
        Client $entity,
        ?string $name = null,
        ?string $email = null,
        ?string $phone = null,
        ?bool $marketingFlag = null
    ): Client {
        if ($name !== null) {
            $entity->setName(trim($name));
        }

        if ($email !== null) {
            $entity->setEmail($email ? trim($email) : null);
        }

        if ($phone !== null) {
            $entity->setPhone($phone ? trim($phone) : null);
        }

        if ($marketingFlag !== null) {
            $entity->setMarketingFlag($marketingFlag);
        }

        return $this->repository->saveEntity($entity);
    }

    /**
     * Delete a client.
     */
    public function delete(Client $entity): bool
    {
        return $this->repository->deleteEntity($entity);
    }
}
