<?php

namespace App\Media\Repository;

use App\Media\Entity\Splashscreen;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class SplashscreenRepository extends Model
{
    protected $table = "splashscreen";

    protected $fillable = [
        "name",
        "category",
        "svg_content",
    ];

    protected $casts = [
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Scope to get only image elements.
     */
    public function scopeImages(Builder $query): Builder
    {
        return $query->where("category", "image");
    }

    /**
     * Scope to get only font elements.
     */
    public function scopeFonts(Builder $query): Builder
    {
        return $query->where("category", "font");
    }

    /**
     * Find all splashscreens ordered by name.
     *
     * @return Splashscreen[]
     */
    public function findAll(): array
    {
        $models = static::query()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a splashscreen by ID.
     */
    public function findById(int $id): ?Splashscreen
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find all image splashscreens.
     *
     * @return Splashscreen[]
     */
    public function findImages(): array
    {
        $models = static::images()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find all font splashscreens.
     *
     * @return Splashscreen[]
     */
    public function findFonts(): array
    {
        $models = static::fonts()->orderBy('name')->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find splashscreens by category.
     *
     * @return Splashscreen[]
     */
    public function findByCategory(?string $category): array
    {
        $query = static::query()->orderBy('name');

        if ($category === 'image') {
            $query->images();
        } elseif ($category === 'font') {
            $query->fonts();
        }

        return $this->modelsToEntities($query->get());
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(Splashscreen $entity): Splashscreen
    {
        if ($entity->getId()) {
            $model = static::find($entity->getId());
        } else {
            $model = new static();
        }

        $model->name = $entity->getName();
        $model->category = $entity->getCategory();
        $model->svg_content = $entity->getSvgContent();
        $model->save();

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(Splashscreen $entity): bool
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
    private function modelToEntity(self $model): Splashscreen
    {
        $entity = new Splashscreen();
        $entity->setId($model->id);
        $entity->setName($model->name);
        $entity->setCategory($model->category);
        $entity->setSvgContent($model->svg_content);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return Splashscreen[]
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
