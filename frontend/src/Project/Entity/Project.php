<?php

namespace App\Project\Entity;

use DateTimeInterface;

class Project
{
    // Status constants
    public const STATUS_CREATED = 'created';
    public const STATUS_PROCESSING = 'processing';
    public const STATUS_DONE = 'done';
    public const STATUS_ARCHIVED = 'archived';

    public const STATUSES = [
        self::STATUS_CREATED,
        self::STATUS_PROCESSING,
        self::STATUS_DONE,
        self::STATUS_ARCHIVED,
    ];

    // Media preference constants
    public const MEDIA_YES = 'yes';
    public const MEDIA_NO = 'no';
    public const MEDIA_MAYBE = 'maybe';

    public const MEDIA_OPTIONS = [
        self::MEDIA_YES,
        self::MEDIA_NO,
        self::MEDIA_MAYBE,
    ];

    // Type constants
    public const TYPE_TANDEM_HC = 'tandem_hc';
    public const TYPE_TANDEM_EXTERNAL = 'tandem_external';
    public const TYPE_AFF = 'aff';
    public const TYPE_FORMATION = 'formation';
    public const TYPE_FUNJUMP = 'funjump';

    public const TYPES = [
        self::TYPE_TANDEM_HC,
        self::TYPE_TANDEM_EXTERNAL,
        self::TYPE_AFF,
        self::TYPE_FORMATION,
        self::TYPE_FUNJUMP,
    ];

    public const TYPE_LABELS = [
        self::TYPE_TANDEM_HC => 'Tandem HC',
        self::TYPE_TANDEM_EXTERNAL => 'Tandem External',
        self::TYPE_AFF => 'AFF',
        self::TYPE_FORMATION => 'Formation',
        self::TYPE_FUNJUMP => 'Funjump',
    ];

    private ?int $id = null;
    private ?string $uuid = null;
    private ?string $qr = null;
    private ?int $clientId = null;
    private ?string $clientName = null;
    private ?int $videographerId = null;
    private ?string $videographerName = null;
    private string $type = self::TYPE_TANDEM_HC;
    private string $status = self::STATUS_CREATED;
    private ?DateTimeInterface $desiredDate = null;
    private string $video = self::MEDIA_MAYBE;
    private string $photo = self::MEDIA_MAYBE;
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

    public function getUuid(): ?string
    {
        return $this->uuid;
    }

    public function setUuid(?string $uuid): self
    {
        $this->uuid = $uuid;
        return $this;
    }

    public function getQr(): ?string
    {
        return $this->qr;
    }

    public function setQr(?string $qr): self
    {
        $this->qr = $qr;
        return $this;
    }

    public function getClientId(): ?int
    {
        return $this->clientId;
    }

    public function setClientId(?int $clientId): self
    {
        $this->clientId = $clientId;
        return $this;
    }

    public function getClientName(): ?string
    {
        return $this->clientName;
    }

    public function setClientName(?string $clientName): self
    {
        $this->clientName = $clientName;
        return $this;
    }

    public function getVideographerId(): ?int
    {
        return $this->videographerId;
    }

    public function setVideographerId(?int $videographerId): self
    {
        $this->videographerId = $videographerId;
        return $this;
    }

    public function getVideographerName(): ?string
    {
        return $this->videographerName;
    }

    public function setVideographerName(?string $videographerName): self
    {
        $this->videographerName = $videographerName;
        return $this;
    }

    public function getType(): string
    {
        return $this->type;
    }

    public function setType(string $type): self
    {
        $this->type = $type;
        return $this;
    }

    public function getTypeLabel(): string
    {
        return self::TYPE_LABELS[$this->type] ?? $this->type;
    }

    public function getStatus(): string
    {
        return $this->status;
    }

    public function setStatus(string $status): self
    {
        $this->status = $status;
        return $this;
    }

    public function getDesiredDate(): ?DateTimeInterface
    {
        return $this->desiredDate;
    }

    public function setDesiredDate(?DateTimeInterface $desiredDate): self
    {
        $this->desiredDate = $desiredDate;
        return $this;
    }

    public function getVideo(): string
    {
        return $this->video;
    }

    public function setVideo(string $video): self
    {
        $this->video = $video;
        return $this;
    }

    public function getPhoto(): string
    {
        return $this->photo;
    }

    public function setPhoto(string $photo): self
    {
        $this->photo = $photo;
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

    public function toArray(): array
    {
        return [
            'id' => $this->id,
            'uuid' => $this->uuid,
            'qr' => $this->qr ? base64_encode($this->qr) : null,
            'client_id' => $this->clientId,
            'client_name' => $this->clientName,
            'videographer_id' => $this->videographerId,
            'videographer_name' => $this->videographerName,
            'type' => $this->type,
            'type_label' => $this->getTypeLabel(),
            'status' => $this->status,
            'desired_date' => $this->desiredDate?->format('Y-m-d'),
            'video' => $this->video,
            'photo' => $this->photo,
            'created_at' => $this->createdAt?->format('Y-m-d H:i:s'),
            'updated_at' => $this->updatedAt?->format('Y-m-d H:i:s'),
        ];
    }
}
