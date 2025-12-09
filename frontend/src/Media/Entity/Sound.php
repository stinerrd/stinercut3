<?php

namespace App\Media\Entity;

use DateTimeInterface;

class Sound
{
    public const TYPE_BODEN = 'boden';
    public const TYPE_PLANE = 'plane';
    public const TYPE_FREEFALL = 'freefall';
    public const TYPE_CANOPY = 'canopy';

    private ?int $id = null;
    private ?string $name = null;
    private ?string $type = null;
    private ?string $description = null;
    private ?string $filePath = null;
    private ?string $waveform = null;
    private ?int $duration = null;
    private ?DateTimeInterface $createdAt = null;
    private ?DateTimeInterface $updatedAt = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function setId(?int $id): self
    {
        $this->id = $id;
        return $this;
    }

    public function getName(): ?string
    {
        return $this->name;
    }

    public function setName(?string $name): self
    {
        $this->name = $name;
        return $this;
    }

    public function getType(): ?string
    {
        return $this->type;
    }

    public function setType(?string $type): self
    {
        $this->type = $type;
        return $this;
    }

    public function getDescription(): ?string
    {
        return $this->description;
    }

    public function setDescription(?string $description): self
    {
        $this->description = $description;
        return $this;
    }

    public function getFilePath(): ?string
    {
        return $this->filePath;
    }

    public function setFilePath(?string $filePath): self
    {
        $this->filePath = $filePath;
        return $this;
    }

    public function getWaveform(): ?string
    {
        return $this->waveform;
    }

    public function setWaveform(?string $waveform): self
    {
        $this->waveform = $waveform;
        return $this;
    }

    public function hasWaveform(): bool
    {
        return $this->waveform !== null && $this->waveform !== '';
    }

    public function getDuration(): ?int
    {
        return $this->duration;
    }

    public function setDuration(?int $duration): self
    {
        $this->duration = $duration;
        return $this;
    }

    public function getCreatedAt(): ?DateTimeInterface
    {
        return $this->createdAt;
    }

    public function setCreatedAt(?DateTimeInterface $createdAt): self
    {
        $this->createdAt = $createdAt;
        return $this;
    }

    public function getUpdatedAt(): ?DateTimeInterface
    {
        return $this->updatedAt;
    }

    public function setUpdatedAt(?DateTimeInterface $updatedAt): self
    {
        $this->updatedAt = $updatedAt;
        return $this;
    }

    public function isBoden(): bool
    {
        return $this->type === self::TYPE_BODEN;
    }

    public function isPlane(): bool
    {
        return $this->type === self::TYPE_PLANE;
    }

    public function isFreefall(): bool
    {
        return $this->type === self::TYPE_FREEFALL;
    }

    public function isCanopy(): bool
    {
        return $this->type === self::TYPE_CANOPY;
    }

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'type' => $this->type,
            'description' => $this->description,
            'file_path' => $this->filePath,
            'has_waveform' => $this->hasWaveform(),
            'duration' => $this->duration,
            'created_at' => $this->createdAt?->format('Y-m-d H:i:s'),
            'updated_at' => $this->updatedAt?->format('Y-m-d H:i:s'),
        ];
    }
}
