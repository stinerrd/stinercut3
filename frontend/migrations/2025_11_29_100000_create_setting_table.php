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
                $table->enum("type", ["string", "integer", "boolean", "json", "splashscreen", "sound", "videopart"])->default("string");
                $table->text("options")->nullable();
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
                "options" => '["h264", "h265", "vp9", "av1"]',
                "category" => "video",
                "label" => "Default Codec",
                "description" => "Default video codec for output files",
            ],
            [
                "key" => "video.default_resolution",
                "value" => "1920x1080",
                "type" => "string",
                "options" => '["1280x720", "1920x1080", "2560x1440", "3840x2160"]',
                "category" => "video",
                "label" => "Default Resolution",
                "description" => "Default output resolution (width x height)",
            ],
            [
                "key" => "video.default_fps",
                "value" => "30",
                "type" => "integer",
                "options" => null,
                "category" => "video",
                "label" => "Default Frame Rate",
                "description" => "Default frames per second for output",
            ],
            [
                "key" => "video.default_bitrate",
                "value" => "8M",
                "type" => "string",
                "options" => null,
                "category" => "video",
                "label" => "Default Bitrate",
                "description" => "Default video bitrate (e.g., 8M, 12M)",
            ],
            // HC template settings
            [
                "key" => "tandem_hc_template.default.splashscreen",
                "value" => null,
                "type" => "splashscreen",
                "options" => null,
                "category" => "tandem_hc_template",
                "label" => "Splashscreen",
                "description" => "Splashscreen overlay for final video",
            ],
            [
                "key" => "tandem_hc_template.default.intro",
                "value" => null,
                "type" => "videopart",
                "options" => null,
                "category" => "tandem_hc_template",
                "label" => "Intro",
                "description" => "Intro clip at the beginning of video",
            ],
            [
                "key" => "tandem_hc_template.default.outro",
                "value" => null,
                "type" => "videopart",
                "options" => null,
                "category" => "tandem_hc_template",
                "label" => "Outro",
                "description" => "Outro clip at the end of video",
            ],
            [
                "key" => "tandem_hc_template.default.transition",
                "value" => "clue",
                "type" => "string",
                "options" => '{"clue":"Smooth crossfade with motion blur","fade":"Simple fade to black transition"}',
                "category" => "tandem_hc_template",
                "label" => "Transitions",
                "description" => "Transition effect between clips",
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
