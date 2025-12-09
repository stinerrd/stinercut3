<?php

namespace App\Media\Repository;

use App\Media\Entity\Videopart;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class VideopartRepository extends Model
{
    protected $table = "videopart";

    protected $fillable = [
        "name",
        "type",
        "description",
        "file_path",
        "thumbnail",
        "duration",
    ];

    protected $casts = [
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Scope to get only intro videos.
     */
    public function scopeIntros(Builder $query): Builder
    {
        return $query->where("type", Videopart::TYPE_INTRO);
    }

    /**
     * Scope to get only outro videos.
     */
    public function scopeOutros(Builder $query): Builder
    {
        return $query->where("type", Videopart::TYPE_OUTRO);
    }

    /**
     * Find all videoparts ordered by name.
     *
     * @return Videopart[]
     */
    public function findAll(): array
    {
        $models = static::query()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a videopart by ID.
     */
    public function findById(int $id): ?Videopart
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find all intro videos.
     *
     * @return Videopart[]
     */
    public function findIntros(): array
    {
        $models = static::intros()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find all outro videos.
     *
     * @return Videopart[]
     */
    public function findOutros(): array
    {
        $models = static::outros()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find videoparts by type.
     *
     * @return Videopart[]
     */
    public function findByType(?string $type): array
    {
        $query = static::query()->orderBy('name');

        if ($type === Videopart::TYPE_INTRO) {
            $query->intros();
        } elseif ($type === Videopart::TYPE_OUTRO) {
            $query->outros();
        }

        return $this->modelsToEntities($query->get());
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(Videopart $entity): Videopart
    {
        if ($entity->getId()) {
            $model = static::find($entity->getId());
        } else {
            $model = new static();
        }

        $model->name = $entity->getName();
        $model->type = $entity->getType();
        $model->description = $entity->getDescription();
        $model->file_path = $entity->getFilePath();
        $model->thumbnail = $entity->getThumbnail();
        $model->duration = $entity->getDuration();
        $model->save();

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(Videopart $entity): bool
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
    private function modelToEntity(self $model): Videopart
    {
        $entity = new Videopart();
        $entity->setId($model->id);
        $entity->setName($model->name);
        $entity->setType($model->type);
        $entity->setDescription($model->description);
        $entity->setFilePath($model->file_path);
        $entity->setThumbnail($model->thumbnail);
        $entity->setDuration($model->duration);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return Videopart[]
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
