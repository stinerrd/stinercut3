<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Setting extends Model
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

    protected $visible = [
        "id",
        "key",
        "value",
        "type",
        "options",
        "category",
        "label",
        "description",
        "created_at",
        "updated_at",
    ];

    protected $casts = [
        "options" => "array",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Get the typed value based on the setting type.
     */
    public function getTypedValue(): mixed
    {
        $value = $this->attributes["value"] ?? null;

        if ($value === null) {
            return null;
        }

        return match ($this->attributes["type"] ?? "string") {
            "integer" => (int) $value,
            "boolean" => filter_var($value, FILTER_VALIDATE_BOOLEAN),
            "json" => json_decode($value, true),
            default => $value,
        };
    }

    /**
     * Get a setting value by key.
     */
    public static function get(string $key, mixed $default = null): mixed
    {
        $setting = static::where("key", $key)->first();

        if (!$setting) {
            return $default;
        }

        return $setting->getTypedValue();
    }

    /**
     * Set a setting value by key.
     */
    public static function set(string $key, mixed $value): bool
    {
        $setting = static::where("key", $key)->first();

        if (!$setting) {
            return false;
        }

        // Convert value to string for storage
        if (is_bool($value)) {
            $value = $value ? "true" : "false";
        } elseif (is_array($value)) {
            $value = json_encode($value);
        } else {
            $value = (string) $value;
        }

        $setting->value = $value;
        return $setting->save();
    }

    // Getters for Symfony PropertyAccessor compatibility
    public function getId(): ?int
    {
        return $this->attributes["id"] ?? null;
    }

    public function getKey(): ?string
    {
        return $this->attributes["key"] ?? null;
    }

    public function getValue(): ?string
    {
        return $this->attributes["value"] ?? null;
    }

    public function getType(): ?string
    {
        return $this->attributes["type"] ?? null;
    }

    public function getCategory(): ?string
    {
        return $this->attributes["category"] ?? null;
    }

    public function getLabel(): ?string
    {
        return $this->attributes["label"] ?? null;
    }

    public function getDescription(): ?string
    {
        return $this->attributes["description"] ?? null;
    }

    public function getOptions(): ?array
    {
        $options = $this->attributes["options"] ?? null;
        return $options ? json_decode($options, true) : null;
    }

    // Setters for Symfony PropertyAccessor compatibility
    public function setKey(?string $value): self
    {
        $this->attributes["key"] = $value;
        return $this;
    }

    public function setValue(?string $value): self
    {
        $this->attributes["value"] = $value;
        return $this;
    }

    public function setType(?string $value): self
    {
        $this->attributes["type"] = $value;
        return $this;
    }

    public function setCategory(?string $value): self
    {
        $this->attributes["category"] = $value;
        return $this;
    }

    public function setLabel(?string $value): self
    {
        $this->attributes["label"] = $value;
        return $this;
    }

    public function setDescription(?string $value): self
    {
        $this->attributes["description"] = $value;
        return $this;
    }
}
