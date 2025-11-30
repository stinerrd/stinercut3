<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table("setting", function (Blueprint $table) {
            $table->text("options")->nullable()->after("type");
        });

        // Update settings with predefined options
        Db::table("setting")
            ->where("key", "video.default_codec")
            ->update(["options" => '["h264", "h265", "vp9", "av1"]']);

        Db::table("setting")
            ->where("key", "video.default_resolution")
            ->update(["options" => '["1280x720", "1920x1080", "2560x1440", "3840x2160"]']);
    }

    public function down(): void
    {
        Schema::table("setting", function (Blueprint $table) {
            $table->dropColumn("options");
        });
    }
};
