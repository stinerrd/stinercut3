<?php

namespace App\Service;

use App\Models\Setting;
use Illuminate\Database\Eloquent\Collection;

class SettingsService
{
    /**
     * Get all settings ordered by category and label.
     */
    public function getAll(): Collection
    {
        return Setting::query()
            ->orderBy('category')
            ->orderBy('label')
            ->get();
    }

    /**
     * Get all settings grouped by category.
     *
     * @return array<string, Collection>
     */
    public function getAllGroupedByCategory(): array
    {
        $settings = $this->getAll();

        return $settings->groupBy('category')->toArray();
    }

    /**
     * Get list of unique categories.
     *
     * @return array<string>
     */
    public function getCategories(): array
    {
        return Setting::query()
            ->distinct()
            ->orderBy('category')
            ->pluck('category')
            ->toArray();
    }

    /**
     * Get a setting by its key.
     */
    public function getByKey(string $key): ?Setting
    {
        return Setting::where('key', $key)->first();
    }

    /**
     * Get a setting value by key with optional default.
     */
    public function getValue(string $key, mixed $default = null): mixed
    {
        return Setting::get($key, $default);
    }

    /**
     * Set a setting value by key.
     */
    public function setValue(string $key, mixed $value): bool
    {
        $setting = $this->getByKey($key);

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

        $setting->value = $value;

        return $setting->save();
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
