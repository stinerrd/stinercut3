<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Asset extends Model
{
    protected $table = "asset";

    public $timestamps = false;

    protected $fillable = [
        "uuid",
        "type",
        "name",
        "path",
    ];

    protected $visible = [
        "id",
        "uuid",
        "type",
        "name",
        "path",
        "created_at",
    ];

    protected $casts = [
        "created_at" => "datetime",
    ];

    // Asset types
    public const TYPE_INTRO = "intro";
    public const TYPE_OUTRO = "outro";
    public const TYPE_WATERMARK = "watermark";
    public const TYPE_AUDIO = "audio";
    public const TYPE_AUDIO_FREEFALL = "audio_freefall";
    public const TYPE_PAX_TEMPLATE = "pax_template";

    public const TYPES = [
        self::TYPE_INTRO,
        self::TYPE_OUTRO,
        self::TYPE_WATERMARK,
        self::TYPE_AUDIO,
        self::TYPE_AUDIO_FREEFALL,
        self::TYPE_PAX_TEMPLATE,
    ];

    // Getters for Symfony PropertyAccessor compatibility
    public function getId(): ?int
    {
        return $this->attributes["id"] ?? null;
    }

    public function getUuid(): ?string
    {
        return $this->attributes["uuid"] ?? null;
    }

    public function getType(): ?string
    {
        return $this->attributes["type"] ?? null;
    }

    public function getName(): ?string
    {
        return $this->attributes["name"] ?? null;
    }

    public function getPath(): ?string
    {
        return $this->attributes["path"] ?? null;
    }

    public function getCreatedAt()
    {
        return isset($this->attributes["created_at"]) ? $this->asDateTime($this->attributes["created_at"]) : null;
    }

    // Setters for Symfony PropertyAccessor compatibility
    public function setUuid(?string $value): self
    {
        $this->attributes["uuid"] = $value;
        return $this;
    }

    public function setType(?string $value): self
    {
        $this->attributes["type"] = $value;
        return $this;
    }

    public function setName(?string $value): self
    {
        $this->attributes["name"] = $value;
        return $this;
    }

    public function setPath(?string $value): self
    {
        $this->attributes["path"] = $value;
        return $this;
    }
}
