<?php

namespace App\Workload\Repository;

use App\Workload\Entity\Workload;
use App\Videographer\Repository\VideographerRepository;
use App\Client\Repository\ClientRepository;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class WorkloadRepository extends Model
{
    protected $table = "workload";

    protected $fillable = [
        "uuid",
        "qr",
        "client_id",
        "videographer_id",
        "type",
        "status",
        "desired_date",
        "video",
        "photo",
    ];

    protected $casts = [
        "client_id" => "integer",
        "videographer_id" => "integer",
        "desired_date" => "date",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Get the videographer associated with this workload.
     */
    public function videographer(): BelongsTo
    {
        return $this->belongsTo(VideographerRepository::class, 'videographer_id');
    }

    /**
     * Get the client associated with this workload.
     */
    public function client(): BelongsTo
    {
        return $this->belongsTo(ClientRepository::class, 'client_id');
    }

    /**
     * Find all workloads.
     *
     * @return Workload[]
     */
    public function findAll(): array
    {
        $models = static::query()
            ->with(['videographer', 'client'])
            ->orderBy('desired_date', 'desc')
            ->orderBy('created_at', 'desc')
            ->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a workload by ID.
     */
    public function findById(int $id): ?Workload
    {
        $model = static::query()->with(['videographer', 'client'])->find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find paginated workloads with filters.
     *
     * @param int $page Page number (1-based)
     * @param int $perPage Items per page
     * @param array $filters Filter criteria
     * @return array{workloads: Workload[], currentPage: int, totalPages: int, total: int, perPage: int}
     */
    public function findPaginated(int $page = 1, int $perPage = 20, array $filters = []): array
    {
        $query = static::query()->with(['videographer', 'client']);

        // Apply filters
        if (!empty($filters['date'])) {
            $query->whereDate('desired_date', $filters['date']);
        }

        if (!empty($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (!empty($filters['videographer_id'])) {
            $query->where('videographer_id', $filters['videographer_id']);
        }

        if (!empty($filters['client_id'])) {
            $query->where('client_id', $filters['client_id']);
        }

        if (!empty($filters['video'])) {
            $query->where('video', $filters['video']);
        }

        if (!empty($filters['photo'])) {
            $query->where('photo', $filters['photo']);
        }

        if (!empty($filters['type'])) {
            $query->where('type', $filters['type']);
        }

        // Get total count
        $total = $query->count();
        $totalPages = $perPage > 0 ? (int) ceil($total / $perPage) : 0;

        // Clamp page to valid range
        $page = max(1, min($page, $totalPages ?: 1));
        $offset = ($page - 1) * $perPage;

        // Get paginated results
        $models = $query
            ->orderBy('desired_date', 'desc')
            ->orderBy('created_at', 'desc')
            ->offset($offset)
            ->limit($perPage)
            ->get();

        return [
            'workloads' => $this->modelsToEntities($models),
            'currentPage' => $page,
            'totalPages' => $totalPages,
            'total' => $total,
            'perPage' => $perPage,
        ];
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(Workload $entity): Workload
    {
        if ($entity->getId()) {
            $model = static::find($entity->getId());
        } else {
            $model = new static();
        }

        $model->uuid = $entity->getUuid();
        $model->qr = $entity->getQr();
        $model->client_id = $entity->getClientId();
        $model->videographer_id = $entity->getVideographerId();
        $model->type = $entity->getType();
        $model->status = $entity->getStatus();
        $model->desired_date = $entity->getDesiredDate();
        $model->video = $entity->getVideo();
        $model->photo = $entity->getPhoto();
        $model->save();

        // Reload with relationships
        $model = static::query()->with(['videographer', 'client'])->find($model->id);

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(Workload $entity): bool
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
    private function modelToEntity(self $model): Workload
    {
        $entity = new Workload();
        $entity->setId($model->id);
        $entity->setUuid($model->uuid);
        $entity->setQr($model->qr);
        $entity->setClientId($model->client_id);
        $entity->setVideographerId($model->videographer_id);
        $entity->setType($model->type ?? Workload::TYPE_TANDEM_HC);
        $entity->setStatus($model->status);
        $entity->setDesiredDate($model->desired_date);
        $entity->setVideo($model->video);
        $entity->setPhoto($model->photo);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        // Set client name if relationship loaded
        if ($model->relationLoaded('client') && $model->client) {
            $entity->setClientName($model->client->name);
        }

        // Set videographer name if relationship loaded
        if ($model->relationLoaded('videographer') && $model->videographer) {
            $entity->setVideographerName($model->videographer->name);
        }

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return Workload[]
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
