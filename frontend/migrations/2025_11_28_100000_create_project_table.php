<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("project")) {
            Schema::create("project", function (Blueprint $table) {
                $table->id();
                $table->char("uuid", 36)->unique()->default(Db::raw("(UUID())"));
                $table->string("name", 255);
                $table->enum("status", ["draft", "processing", "completed", "error"])->default("draft");
                $table->json("settings")->nullable();
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("status");
                $table->index("created_at");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("project");
    }
};
