<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("project")) {
            Schema::create("project", function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger("client_id")->nullable();
                $table->char("uuid", 36)->unique();
                $table->binary("qr")->nullable();
                $table->unsignedBigInteger("videographer_id")->nullable();
                $table->string("type", 50)->default("tandem_hc");
                $table->string("status", 50)->default("created");
                $table->date("desired_date")->default(DB::raw("(CURRENT_DATE)"));
                $table->enum("video", ["yes", "no", "maybe"])->default("maybe");
                $table->enum("photo", ["yes", "no", "maybe"])->default("maybe");
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                // Foreign keys
                $table->foreign("client_id")
                    ->references("id")
                    ->on("client")
                    ->nullOnDelete();

                $table->foreign("videographer_id")
                    ->references("id")
                    ->on("videographer")
                    ->nullOnDelete();

                // Indexes
                $table->index("client_id", "idx_project_client_id");
                $table->index("videographer_id", "idx_project_videographer");
                $table->index("type", "idx_project_type");
                $table->index("status", "idx_project_status");
                $table->index("desired_date", "idx_project_desired_date");
                $table->index("video", "idx_project_video");
                $table->index("photo", "idx_project_photo");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("project");
    }
};
