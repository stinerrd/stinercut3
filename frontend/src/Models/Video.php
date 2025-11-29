<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Video extends Model
{
    protected $table = "video";

    protected $fillable = [
        "uuid",
        "project_id",
        "filename",
        "path",
        "duration",
        "width",
        "height",
        "codec",
        "fps",
        "order",
        "in_point",
        "out_point",
    ];

    protected $visible = [
        "id",
        "uuid",
        "project_id",
        "filename",
        "path",
        "duration",
        "width",
        "height",
        "codec",
        "fps",
        "order",
        "in_point",
        "out_point",
        "created_at",
        "updated_at",
    ];

    protected $casts = [
        "duration" => "float",
        "width" => "integer",
        "height" => "integer",
        "fps" => "float",
        "order" => "integer",
        "in_point" => "float",
        "out_point" => "float",
        "created_at" => "datetime",
        "updated_at" => "datetime",
    ];

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
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

    public function getProjectId(): ?int
    {
        return $this->attributes["project_id"] ?? null;
    }

    public function getFilename(): ?string
    {
        return $this->attributes["filename"] ?? null;
    }

    public function getPath(): ?string
    {
        return $this->attributes["path"] ?? null;
    }

    public function getDuration(): ?float
    {
        return $this->attributes["duration"] ?? null;
    }

    public function getWidth(): ?int
    {
        return $this->attributes["width"] ?? null;
    }

    public function getHeight(): ?int
    {
        return $this->attributes["height"] ?? null;
    }

    public function getCodec(): ?string
    {
        return $this->attributes["codec"] ?? null;
    }

    public function getFps(): ?float
    {
        return $this->attributes["fps"] ?? null;
    }

    public function getOrder(): ?int
    {
        return $this->attributes["order"] ?? null;
    }

    public function getInPoint(): ?float
    {
        return $this->attributes["in_point"] ?? null;
    }

    public function getOutPoint(): ?float
    {
        return $this->attributes["out_point"] ?? null;
    }

    // Setters for Symfony PropertyAccessor compatibility
    public function setUuid(?string $value): self
    {
        $this->attributes["uuid"] = $value;
        return $this;
    }

    public function setProjectId(?int $value): self
    {
        $this->attributes["project_id"] = $value;
        return $this;
    }

    public function setFilename(?string $value): self
    {
        $this->attributes["filename"] = $value;
        return $this;
    }

    public function setPath(?string $value): self
    {
        $this->attributes["path"] = $value;
        return $this;
    }

    public function setDuration(?float $value): self
    {
        $this->attributes["duration"] = $value;
        return $this;
    }

    public function setWidth(?int $value): self
    {
        $this->attributes["width"] = $value;
        return $this;
    }

    public function setHeight(?int $value): self
    {
        $this->attributes["height"] = $value;
        return $this;
    }

    public function setCodec(?string $value): self
    {
        $this->attributes["codec"] = $value;
        return $this;
    }

    public function setFps(?float $value): self
    {
        $this->attributes["fps"] = $value;
        return $this;
    }

    public function setOrder(?int $value): self
    {
        $this->attributes["order"] = $value;
        return $this;
    }

    public function setInPoint(?float $value): self
    {
        $this->attributes["in_point"] = $value;
        return $this;
    }

    public function setOutPoint(?float $value): self
    {
        $this->attributes["out_point"] = $value;
        return $this;
    }
}
