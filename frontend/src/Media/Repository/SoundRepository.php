<?php

namespace App\Media\Repository;

use App\Media\Entity\Sound;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class SoundRepository extends Model
{
    protected $table = "sound";

    protected $fillable = [
        "name",
        "type",
        "description",
        "file_path",
        "waveform",
        "duration",
    ];

    protected $casts = [
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Scope to get only boden sounds.
     */
    public function scopeBoden(Builder $query): Builder
    {
        return $query->where("type", Sound::TYPE_BODEN);
    }

    /**
     * Scope to get only plane sounds.
     */
    public function scopePlane(Builder $query): Builder
    {
        return $query->where("type", Sound::TYPE_PLANE);
    }

    /**
     * Scope to get only freefall sounds.
     */
    public function scopeFreefall(Builder $query): Builder
    {
        return $query->where("type", Sound::TYPE_FREEFALL);
    }

    /**
     * Scope to get only canopy sounds.
     */
    public function scopeCanopy(Builder $query): Builder
    {
        return $query->where("type", Sound::TYPE_CANOPY);
    }

    /**
     * Find all sounds ordered by name.
     *
     * @return Sound[]
     */
    public function findAll(): array
    {
        $models = static::query()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a sound by ID.
     */
    public function findById(int $id): ?Sound
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find all boden sounds.
     *
     * @return Sound[]
     */
    public function findBoden(): array
    {
        $models = static::boden()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find all plane sounds.
     *
     * @return Sound[]
     */
    public function findPlane(): array
    {
        $models = static::plane()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find all freefall sounds.
     *
     * @return Sound[]
     */
    public function findFreefall(): array
    {
        $models = static::freefall()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find all canopy sounds.
     *
     * @return Sound[]
     */
    public function findCanopy(): array
    {
        $models = static::canopy()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find sounds by type.
     *
     * @return Sound[]
     */
    public function findByType(?string $type): array
    {
        $query = static::query()->orderBy('name');

        if ($type === Sound::TYPE_BODEN) {
            $query->boden();
        } elseif ($type === Sound::TYPE_PLANE) {
            $query->plane();
        } elseif ($type === Sound::TYPE_FREEFALL) {
            $query->freefall();
        } elseif ($type === Sound::TYPE_CANOPY) {
            $query->canopy();
        }

        return $this->modelsToEntities($query->get());
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(Sound $entity): Sound
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
        $model->waveform = $entity->getWaveform();
        $model->duration = $entity->getDuration();
        $model->save();

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(Sound $entity): bool
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
    private function modelToEntity(self $model): Sound
    {
        $entity = new Sound();
        $entity->setId($model->id);
        $entity->setName($model->name);
        $entity->setType($model->type);
        $entity->setDescription($model->description);
        $entity->setFilePath($model->file_path);
        $entity->setWaveform($model->waveform);
        $entity->setDuration($model->duration);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return Sound[]
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
