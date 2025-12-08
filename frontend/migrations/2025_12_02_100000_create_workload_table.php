<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("workload")) {
            Schema::create("workload", function (Blueprint $table) {
                $table->id();
                $table->char("uuid", 36)->unique();
                $table->string("name", 255);
                $table->string("email", 255)->nullable();
                $table->string("phone", 50)->nullable();
                $table->unsignedBigInteger("tandem_master_id")->nullable();
                $table->string("status", 50)->default("created");
                $table->date("desired_date")->default(DB::raw("(CURRENT_DATE)"));
                $table->enum("video", ["yes", "no", "maybe"])->default("maybe");
                $table->enum("photo", ["yes", "no", "maybe"])->default("maybe");
                $table->boolean("marketing_flag")->default(false);
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                // Foreign key with ON DELETE SET NULL
                $table->foreign("tandem_master_id")
                    ->references("id")
                    ->on("tandem_master")
                    ->nullOnDelete();

                // Indexes
                $table->index("tandem_master_id", "idx_workload_tandem_master");
                $table->index("status", "idx_workload_status");
                $table->index("desired_date", "idx_workload_desired_date");
                $table->index("video", "idx_workload_video");
                $table->index("photo", "idx_workload_photo");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("workload");
    }
};
