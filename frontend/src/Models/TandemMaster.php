<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TandemMaster extends Model
{
    protected $table = "tandem_master";

    protected $fillable = [
        "name",
        "image",
        "image_mime",
        "active",
    ];

    protected $visible = [
        "id",
        "name",
        "active",
        "has_image",
        "created_at",
        "updated_at",
    ];

    protected $appends = [
        "has_image",
    ];

    protected $casts = [
        "active" => "boolean",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    /**
     * Get only active tandem masters.
     */
    public static function active()
    {
        return static::where("active", true)->get();
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

    public function getImage()
    {
        return $this->attributes["image"] ?? null;
    }

    public function getImageMime(): ?string
    {
        return $this->attributes["image_mime"] ?? null;
    }

    public function getActive(): bool
    {
        return (bool) ($this->attributes["active"] ?? false);
    }

    public function getHasImageAttribute(): bool
    {
        return !empty($this->attributes["image"]);
    }

    public function getHasImage(): bool
    {
        return $this->getHasImageAttribute();
    }

    // Setters for Symfony PropertyAccessor compatibility
    public function setName(?string $value): self
    {
        $this->attributes["name"] = $value;
        return $this;
    }

    public function setImage($value): self
    {
        $this->attributes["image"] = $value;
        return $this;
    }

    public function setImageMime(?string $value): self
    {
        $this->attributes["image_mime"] = $value;
        return $this;
    }

    public function setActive(bool $value): self
    {
        $this->attributes["active"] = $value;
        return $this;
    }
}
