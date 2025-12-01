<?php

namespace App\TandemMaster\Repository;

use App\TandemMaster\Entity\TandemMaster;
use Illuminate\Database\Eloquent\Model;

class TandemMasterRepository extends Model
{
    protected $table = "tandem_master";

    protected $fillable = [
        "name",
        "image",
        "image_mime",
        "active",
    ];

    protected $casts = [
        "active" => "boolean",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Find all tandem masters.
     *
     * @return TandemMaster[]
     */
    public function findAll(): array
    {
        $models = static::query()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a tandem master by ID.
     */
    public function findById(int $id): ?TandemMaster
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find all active tandem masters.
     *
     * @return TandemMaster[]
     */
    public function findActive(): array
    {
        $models = static::query()
            ->where('active', true)
            ->orderBy('name')
            ->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(TandemMaster $entity): TandemMaster
    {
        if ($entity->getId()) {
            $model = static::find($entity->getId());
        } else {
            $model = new static();
        }

        $model->name = $entity->getName();
        $model->active = $entity->isActive();
        $model->image = $entity->getImage();
        $model->image_mime = $entity->getImageMime();
        $model->save();

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(TandemMaster $entity): bool
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
     * Get raw image data for a tandem master.
     */
    public function getImageData(int $id): ?array
    {
        $model = static::find($id);
        if (!$model || empty($model->image)) {
            return null;
        }

        return [
            'data' => $model->image,
            'mime' => $model->image_mime ?? 'image/jpeg',
        ];
    }

    /**
     * Convert Eloquent model to Entity.
     */
    private function modelToEntity(self $model): TandemMaster
    {
        $entity = new TandemMaster();
        $entity->setId($model->id);
        $entity->setName($model->name);
        $entity->setActive((bool) $model->active);
        $entity->setImage($model->image);
        $entity->setImageMime($model->image_mime);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return TandemMaster[]
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
