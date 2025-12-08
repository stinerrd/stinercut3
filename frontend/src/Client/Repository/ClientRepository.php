<?php

declare(strict_types=1);

namespace App\Client\Repository;

use App\Client\Entity\Client;
use Illuminate\Database\Eloquent\Model;

class ClientRepository extends Model
{
    protected $table = 'client';

    protected $fillable = [
        'name',
        'email',
        'phone',
        'marketing_flag',
    ];

    protected $casts = [
        'marketing_flag' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    /**
     * Find all clients.
     *
     * @return Client[]
     */
    public function findAll(): array
    {
        $models = static::query()
            ->orderBy('name', 'asc')
            ->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a client by ID.
     */
    public function findById(int $id): ?Client
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find paginated clients with filters.
     *
     * @param int $page Page number (1-based)
     * @param int $perPage Items per page
     * @param array $filters Filter criteria
     * @return array{clients: Client[], currentPage: int, totalPages: int, total: int, perPage: int}
     */
    public function findPaginated(int $page = 1, int $perPage = 20, array $filters = []): array
    {
        $query = static::query();

        // Apply filters
        if (!empty($filters['name'])) {
            $query->where('name', 'like', '%' . $filters['name'] . '%');
        }

        if (isset($filters['marketing_flag']) && $filters['marketing_flag'] !== '') {
            $query->where('marketing_flag', (bool) $filters['marketing_flag']);
        }

        // Get total count
        $total = $query->count();
        $totalPages = $perPage > 0 ? (int) ceil($total / $perPage) : 0;

        // Clamp page to valid range
        $page = max(1, min($page, $totalPages ?: 1));
        $offset = ($page - 1) * $perPage;

        // Get paginated results
        $models = $query
            ->orderBy('name', 'asc')
            ->offset($offset)
            ->limit($perPage)
            ->get();

        return [
            'clients' => $this->modelsToEntities($models),
            'currentPage' => $page,
            'totalPages' => $totalPages,
            'total' => $total,
            'perPage' => $perPage,
        ];
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(Client $entity): Client
    {
        if ($entity->getId()) {
            $model = static::find($entity->getId());
        } else {
            $model = new static();
        }

        $model->name = $entity->getName();
        $model->email = $entity->getEmail();
        $model->phone = $entity->getPhone();
        $model->marketing_flag = $entity->getMarketingFlag();
        $model->save();

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(Client $entity): bool
    {
        if (!$entity->getId()) {
            return false;
        }

        $model = static::find($entity->getId());
        if (!$model) {
            return false;
        }

        return $model->delete();
    }

    /**
     * Convert Eloquent model to Entity.
     */
    private function modelToEntity(self $model): Client
    {
        $entity = new Client();
        $entity->setId($model->id);
        $entity->setName($model->name);
        $entity->setEmail($model->email);
        $entity->setPhone($model->phone);
        $entity->setMarketingFlag((bool) $model->marketing_flag);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return Client[]
     */
    private function modelsToEntities($models): array
    {
        $entities = [];
        foreach ($models as $model) {
            $entities[] = $this->modelToEntity($model);
        }
        return $entities;
    }
}
