<?php

namespace App\Settings\Service;

use App\Settings\Entity\Setting;
use App\Settings\Repository\SettingRepository;

class SettingService
{
    public function __construct(
        private readonly SettingRepository $repository,
    ) {
    }

    /**
     * Get all settings ordered by category and label.
     *
     * @return Setting[]
     */
    public function getAll(): array
    {
        return $this->repository->findAll();
    }

    /**
     * Get all settings grouped by category.
     *
     * @return array<string, Setting[]>
     */
    public function getAllGroupedByCategory(): array
    {
        $settings = $this->repository->findAll();
        $grouped = [];

        foreach ($settings as $setting) {
            $category = $setting->getCategory() ?? 'general';
            if (!isset($grouped[$category])) {
                $grouped[$category] = [];
            }
            $grouped[$category][] = $setting;
        }

        return $grouped;
    }

    /**
     * Get list of unique categories.
     *
     * @return string[]
     */
    public function getCategories(): array
    {
        return $this->repository->getCategories();
    }

    /**
     * Find a setting by ID.
     */
    public function find(int $id): ?Setting
    {
        return $this->repository->findById($id);
    }

    /**
     * Get a setting by its key.
     */
    public function getByKey(string $key): ?Setting
    {
        return $this->repository->findByKey($key);
    }

    /**
     * Get a setting value by key with optional default.
     */
    public function getValue(string $key, mixed $default = null): mixed
    {
        return SettingRepository::get($key, $default);
    }

    /**
     * Set a setting value by key.
     */
    public function setValue(string $key, mixed $value): bool
    {
        $setting = $this->repository->findByKey($key);

        if (!$setting) {
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

        $setting->setValue($value);

        $this->repository->saveEntity($setting);

        return true;
    }

    /**
     * Update multiple settings at once.
     *
     * @param array<string, mixed> $settings Key-value pairs
     * @return array{updated: array<string>, errors: array<string>}
     */
    public function setValues(array $settings): array
    {
        $updated = [];
        $errors = [];

        foreach ($settings as $key => $value) {
            if ($this->setValue($key, $value)) {
                $updated[] = $key;
            } else {
                $errors[] = "Setting not found: $key";
            }
        }

        return [
            'updated' => $updated,
            'errors' => $errors,
        ];
    }
}
