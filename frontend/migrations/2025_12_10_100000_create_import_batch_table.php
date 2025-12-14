<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("import_batch")) {
            Schema::create("import_batch", function (Blueprint $table) {
                $table->id();
                $table->string("uuid", 36)->unique();

                // Analysis results
                $table->integer("total_files")->default(0);
                $table->integer("analyzed_files")->default(0);
                $table->integer("detected_qr_count")->default(0);
                $table->integer("detected_freefall_count")->default(0);

                // Status: pending, analyzing, resolved, needs_manual, error
                $table->string("status", 50)->default("pending");
                // Resolution type: auto_single, auto_multi, manual, unresolved
                $table->string("resolution_type", 50)->nullable();

                $table->text("error_message")->nullable();

                // SD card mount path (for organizing SD card after resolution)
                $table->string("mount_path", 255)->nullable();

                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("status");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("import_batch");
    }
};
