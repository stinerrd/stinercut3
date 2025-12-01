<?php

namespace App\Settings\Repository;

use App\Settings\Entity\Setting;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class SettingRepository extends Model
{
    protected $table = "setting";

    protected $fillable = [
        "key",
        "value",
        "type",
        "options",
        "category",
        "label",
        "description",
    ];

    protected $casts = [
        "options" => "array",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Find all settings ordered by category and label.
     *
     * @return Setting[]
     */
    public function findAll(): array
    {
        $models = static::query()
            ->orderBy('category')
            ->orderBy('label')
            ->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Find a setting by ID.
     */
    public function findById(int $id): ?Setting
    {
        $model = static::find($id);
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find a setting by key.
     */
    public function findByKey(string $key): ?Setting
    {
        $model = static::where('key', $key)->first();
        return $model ? $this->modelToEntity($model) : null;
    }

    /**
     * Find settings by category.
     *
     * @return Setting[]
     */
    public function findByCategory(string $category): array
    {
        $models = static::query()
            ->where('category', $category)
            ->orderBy('label')
            ->get();
        return $this->modelsToEntities($models);
    }

    /**
     * Get list of unique categories.
     *
     * @return string[]
     */
    public function getCategories(): array
    {
        return static::query()
            ->distinct()
            ->orderBy('category')
            ->pluck('category')
            ->toArray();
    }

    /**
     * Save an entity to the database.
     */
    public function saveEntity(Setting $entity): Setting
    {
        if ($entity->getId()) {
            $model = static::find($entity->getId());
        } else {
            $model = new static();
        }

        $model->key = $entity->getKey();
        $model->value = $entity->getValue();
        $model->type = $entity->getType();
        $model->options = $entity->getOptions();
        $model->category = $entity->getCategory();
        $model->label = $entity->getLabel();
        $model->description = $entity->getDescription();
        $model->save();

        return $this->modelToEntity($model);
    }

    /**
     * Delete an entity from the database.
     */
    public function deleteEntity(Setting $entity): bool
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
     * Get a setting value by key (static helper).
     */
    public static function get(string $key, mixed $default = null): mixed
    {
        $model = static::where('key', $key)->first();

        if (!$model) {
            return $default;
        }

        $value = $model->value;
        if ($value === null) {
            return $default;
        }

        return match ($model->type ?? 'string') {
            'integer' => (int) $value,
            'boolean' => filter_var($value, FILTER_VALIDATE_BOOLEAN),
            'json' => json_decode($value, true),
            default => $value,
        };
    }

    /**
     * Set a setting value by key (static helper).
     */
    public static function set(string $key, mixed $value): bool
    {
        $model = static::where('key', $key)->first();

        if (!$model) {
            return false;
        }

        // Convert value to string for storage
        if (is_bool($value)) {
            $value = $value ? 'true' : 'false';
        } elseif (is_array($value)) {
            $value = json_encode($value);
        } else {
            $value = (string) $value;
        }

        $model->value = $value;
        return $model->save();
    }

    /**
     * Convert Eloquent model to Entity.
     */
    private function modelToEntity(self $model): Setting
    {
        $entity = new Setting();
        $entity->setId($model->id);
        $entity->setKey($model->key);
        $entity->setValue($model->value);
        $entity->setType($model->type);
        $entity->setOptions($model->options);
        $entity->setCategory($model->category);
        $entity->setLabel($model->label);
        $entity->setDescription($model->description);
        $entity->setCreatedAt($model->created_at);
        $entity->setUpdatedAt($model->updated_at);

        return $entity;
    }

    /**
     * Convert collection of models to array of entities.
     *
     * @return Setting[]
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
