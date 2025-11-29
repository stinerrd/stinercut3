<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("job")) {
            Schema::create("job", function (Blueprint $table) {
                $table->id();
                $table->char("uuid", 36)->unique()->default(Db::raw("(UUID())"));
                $table->unsignedBigInteger("project_id");
                $table->enum("status", ["pending", "processing", "completed", "failed", "cancelled"])->default("pending");
                $table->integer("progress")->default(0);
                $table->timestamp("started_at")->nullable();
                $table->timestamp("completed_at")->nullable();
                $table->string("output_path", 512)->nullable();
                $table->text("error_message")->nullable();
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->foreign("project_id")->references("id")->on("project")->onDelete("cascade");
                $table->index("project_id");
                $table->index("status");
                $table->index(["project_id", "status"]);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("job");
    }
};
