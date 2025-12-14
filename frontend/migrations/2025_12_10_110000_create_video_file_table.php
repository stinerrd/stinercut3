<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("video_file")) {
            Schema::create("video_file", function (Blueprint $table) {
                $table->id();
                $table->string("uuid", 36)->unique();

                // Folder tracking
                $table->string("import_folder_uuid", 36);
                $table->string("current_folder_uuid", 255);  // CLIENT_NAME_UUID format
                $table->string("filepath", 500);
                $table->string("original_filename", 255);

                // Video metadata
                $table->decimal("duration", 10, 3)->nullable();
                $table->bigInteger("file_size_bytes")->nullable();
                $table->integer("width")->nullable();
                $table->integer("height")->nullable();
                $table->decimal("fps", 6, 3)->nullable();
                $table->string("codec", 50)->nullable();
                $table->dateTime("recorded_at")->nullable();

                // Classification
                $table->string("dominant_classification", 50)->default("unknown");
                $table->decimal("classification_confidence", 5, 4)->nullable();

                // QR Detection
                $table->text("qr_content")->nullable();
                $table->string("detected_project_uuid", 36)->nullable();
                $table->bigInteger("project_id")->unsigned()->nullable();

                // Processing status: pending, analyzing, analyzed, matched, error
                $table->string("status", 50)->default("pending");
                $table->text("error_message")->nullable();

                // Jump assignment (for multi-jump scenarios)
                $table->integer("jump_number")->nullable();

                // Import source: gopro, upload
                $table->string("import_source", 50)->default("gopro");

                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("import_folder_uuid");
                $table->index("current_folder_uuid");
                $table->index("status");
                $table->index("detected_project_uuid");
                $table->index("project_id");
            });

            // Add MEDIUMBLOB column for thumbnail (Blueprint doesn't support MEDIUMBLOB directly)
            Schema::getConnection()->statement("ALTER TABLE video_file ADD COLUMN thumbnail MEDIUMBLOB NULL AFTER jump_number");
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("video_file");
    }
};
