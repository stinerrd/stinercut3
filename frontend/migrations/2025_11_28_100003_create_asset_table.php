<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("asset")) {
            Schema::create("asset", function (Blueprint $table) {
                $table->id();
                $table->char("uuid", 36)->unique()->default(Db::raw("(UUID())"));
                $table->enum("type", ["intro", "outro", "watermark", "audio", "audio_freefall", "pax_template"]);
                $table->string("name", 255);
                $table->string("path", 512);
                $table->timestamp("created_at")->useCurrent();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("type");
                $table->index(["type", "name"]);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("asset");
    }
};
