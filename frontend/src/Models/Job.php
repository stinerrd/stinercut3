<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Job extends Model
{
    protected $table = "job";

    protected $fillable = [
        "uuid",
        "project_id",
        "status",
        "progress",
        "started_at",
        "completed_at",
        "output_path",
        "error_message",
    ];

    protected $visible = [
        "id",
        "uuid",
        "project_id",
        "status",
        "progress",
        "started_at",
        "completed_at",
        "output_path",
        "error_message",
        "created_at",
        "updated_at",
    ];

    protected $casts = [
        "progress" => "integer",
        "started_at" => "datetime",
        "completed_at" => "datetime",
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

    public function getStatus(): ?string
    {
        return $this->attributes["status"] ?? null;
    }

    public function getProgress(): ?int
    {
        return $this->attributes["progress"] ?? null;
    }

    public function getStartedAt()
    {
        return isset($this->attributes["started_at"]) ? $this->asDateTime($this->attributes["started_at"]) : null;
    }

    public function getCompletedAt()
    {
        return isset($this->attributes["completed_at"]) ? $this->asDateTime($this->attributes["completed_at"]) : null;
    }

    public function getOutputPath(): ?string
    {
        return $this->attributes["output_path"] ?? null;
    }

    public function getErrorMessage(): ?string
    {
        return $this->attributes["error_message"] ?? null;
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

    public function setStatus(?string $value): self
    {
        $this->attributes["status"] = $value;
        return $this;
    }

    public function setProgress(?int $value): self
    {
        $this->attributes["progress"] = $value;
        return $this;
    }

    public function setStartedAt($value): self
    {
        $this->attributes["started_at"] = $value;
        return $this;
    }

    public function setCompletedAt($value): self
    {
        $this->attributes["completed_at"] = $value;
        return $this;
    }

    public function setOutputPath(?string $value): self
    {
        $this->attributes["output_path"] = $value;
        return $this;
    }

    public function setErrorMessage(?string $value): self
    {
        $this->attributes["error_message"] = $value;
        return $this;
    }
}
