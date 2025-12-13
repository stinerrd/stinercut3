<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Project extends Model
{
    protected $table = "project";

    protected $fillable = [
        "uuid",
        "name",
        "status",
        "settings",
    ];

    protected $visible = [
        "id",
        "uuid",
        "name",
        "status",
        "settings",
        "created_at",
        "updated_at",
    ];

    protected $casts = [
        "settings" => "array",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    public function videos(): HasMany
    {
        return $this->hasMany(Video::class);
    }

    // Getters for Symfony PropertyAccessor compatibility
    public function getId(): ?int
    {
        return $this->attributes["id"] ?? null;
    }

    public function getUuid(): ?string
    {
        return $this->attributes["uuid"] ?? null;
    }

    public function getName(): ?string
    {
        return $this->attributes["name"] ?? null;
    }

    public function getStatus(): ?string
    {
        return $this->attributes["status"] ?? null;
    }

    public function getSettings(): ?array
    {
        $value = $this->attributes["settings"] ?? null;
        return $value ? json_decode($value, true) : null;
    }

    // Setters for Symfony PropertyAccessor compatibility
    public function setUuid(?string $value): self
    {
        $this->attributes["uuid"] = $value;
        return $this;
    }

    public function setName(?string $value): self
    {
        $this->attributes["name"] = $value;
        return $this;
    }

    public function setStatus(?string $value): self
    {
        $this->attributes["status"] = $value;
        return $this;
    }

    public function setSettings(?array $value): self
    {
        $this->attributes["settings"] = $value ? json_encode($value) : null;
        return $this;
    }
}
