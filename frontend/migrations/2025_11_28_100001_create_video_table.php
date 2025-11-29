<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("video")) {
            Schema::create("video", function (Blueprint $table) {
                $table->id();
                $table->char("uuid", 36)->unique()->default(Db::raw("(UUID())"));
                $table->unsignedBigInteger("project_id");
                $table->string("filename", 255);
                $table->string("path", 512);
                $table->float("duration")->nullable();
                $table->integer("width")->nullable();
                $table->integer("height")->nullable();
                $table->string("codec", 50)->nullable();
                $table->float("fps")->nullable();
                $table->integer("order")->default(0);
                $table->float("in_point")->nullable();
                $table->float("out_point")->nullable();
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->foreign("project_id")->references("id")->on("project")->onDelete("cascade");
                $table->index("project_id");
                $table->index(["project_id", "order"]);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("video");
    }
};
