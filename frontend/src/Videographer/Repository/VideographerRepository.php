<?php

namespace App\Videographer\Repository;

use App\Videographer\Entity\Videographer;
use Illuminate\Database\Eloquent\Model;

class VideographerRepository extends Model
{
    protected $table = "videographer";

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
     * Find all videographers.
     *
     * @return Videographer[]
     */
    public function findAll(): array
    {
        $models = static::query()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a videographer by ID.
     */
    public function findById(int $id): ?Videographer
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find all active videographers.
     *
     * @return Videographer[]
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
    public function saveEntity(Videographer $entity): Videographer
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
    public function deleteEntity(Videographer $entity): bool
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
     * Get raw image data for a videographer.
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
    private function modelToEntity(self $model): Videographer
    {
        $entity = new Videographer();
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
     * @return Videographer[]
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
