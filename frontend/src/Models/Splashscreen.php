<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Builder;

class Splashscreen extends Model
{
    protected $table = "splashscreen";

    protected $fillable = [
        "name",
        "category",
        "svg_content",
    ];

    protected $visible = [
        "id",
        "name",
        "category",
        "created_at",
        "updated_at",
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

    // Getters for Symfony PropertyAccessor compatibility
    public function getId(): ?int
    {
        return $this->attributes["id"] ?? null;
    }

    public function getName(): ?string
    {
        return $this->attributes["name"] ?? null;
    }

    public function getCategory(): ?string
    {
        return $this->attributes["category"] ?? null;
    }

    public function getSvgContent(): ?string
    {
        return $this->attributes["svg_content"] ?? null;
    }

    // Setters for Symfony PropertyAccessor compatibility
    public function setName(?string $value): self
    {
        $this->attributes["name"] = $value;
        return $this;
    }

    public function setCategory(?string $value): self
    {
        $this->attributes["category"] = $value;
        return $this;
    }

    public function setSvgContent(?string $value): self
    {
        $this->attributes["svg_content"] = $value;
        return $this;
    }
}
