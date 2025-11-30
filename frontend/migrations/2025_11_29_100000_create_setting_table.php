<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("setting")) {
            Schema::create("setting", function (Blueprint $table) {
                $table->id();
                $table->string("key", 255)->unique();
                $table->text("value")->nullable();
                $table->enum("type", ["string", "integer", "boolean", "json"])->default("string");
                $table->string("category", 100);
                $table->string("label", 255);
                $table->text("description")->nullable();
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("category");
            });

            // Seed initial settings
            $this->seedSettings();
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("setting");
    }

    private function seedSettings(): void
    {
        $settings = [
            // Video settings
            [
                "key" => "video.default_codec",
                "value" => "h264",
                "type" => "string",
                "category" => "video",
                "label" => "Default Codec",
                "description" => "Default video codec for output files",
            ],
            [
                "key" => "video.default_resolution",
                "value" => "1920x1080",
                "type" => "string",
                "category" => "video",
                "label" => "Default Resolution",
                "description" => "Default output resolution (width x height)",
            ],
            [
                "key" => "video.default_fps",
                "value" => "30",
                "type" => "integer",
                "category" => "video",
                "label" => "Default Frame Rate",
                "description" => "Default frames per second for output",
            ],
            [
                "key" => "video.default_bitrate",
                "value" => "8M",
                "type" => "string",
                "category" => "video",
                "label" => "Default Bitrate",
                "description" => "Default video bitrate (e.g., 8M, 12M)",
            ],
            // Storage settings
            [
                "key" => "storage.upload_path",
                "value" => "/shared-videos/uploads",
                "type" => "string",
                "category" => "storage",
                "label" => "Upload Path",
                "description" => "Directory for uploaded video files",
            ],
            [
                "key" => "storage.output_path",
                "value" => "/shared-videos/output",
                "type" => "string",
                "category" => "storage",
                "label" => "Output Path",
                "description" => "Directory for processed video files",
            ],
            [
                "key" => "storage.temp_path",
                "value" => "/shared-videos/temp",
                "type" => "string",
                "category" => "storage",
                "label" => "Temp Path",
                "description" => "Directory for temporary processing files",
            ],
            [
                "key" => "storage.max_upload_size",
                "value" => "5368709120",
                "type" => "integer",
                "category" => "storage",
                "label" => "Max Upload Size",
                "description" => "Maximum upload file size in bytes (default: 5GB)",
            ],
        ];

        $now = date("Y-m-d H:i:s");
        foreach ($settings as &$setting) {
            $setting["created_at"] = $now;
            $setting["updated_at"] = $now;
        }

        Db::table("setting")->insert($settings);
    }
};
