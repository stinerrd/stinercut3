<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("tandem_master")) {
            Schema::create("tandem_master", function (Blueprint $table) {
                $table->id();
                $table->string("name", 255);
                $table->binary("image")->nullable();
                $table->string("image_mime", 50)->nullable();
                $table->boolean("active")->default(true);
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("active");
            });
        }

        // Add avatar settings
        $this->seedSettings();
    }

    public function down(): void
    {
        Schema::dropIfExists("tandem_master");
    }

    private function seedSettings(): void
    {
        $settings = [
            [
                "key" => "avatar.max_upload_size",
                "value" => "5242880",
                "type" => "integer",
                "category" => "avatar",
                "label" => "Max Avatar Upload Size",
                "description" => "Maximum avatar upload size in bytes (default: 5MB)",
            ],
            [
                "key" => "avatar.width",
                "value" => "150",
                "type" => "integer",
                "category" => "avatar",
                "label" => "Avatar Width",
                "description" => "Avatar image width in pixels",
            ],
            [
                "key" => "avatar.height",
                "value" => "150",
                "type" => "integer",
                "category" => "avatar",
                "label" => "Avatar Height",
                "description" => "Avatar image height in pixels",
            ],
        ];

        $now = date("Y-m-d H:i:s");
        foreach ($settings as &$setting) {
            $setting["created_at"] = $now;
            $setting["updated_at"] = $now;
        }

        // Check if settings already exist before inserting
        foreach ($settings as $setting) {
            $exists = Db::table("setting")->where("key", $setting["key"])->exists();
            if (!$exists) {
                Db::table("setting")->insert([$setting]);
            }
        }
    }
};
