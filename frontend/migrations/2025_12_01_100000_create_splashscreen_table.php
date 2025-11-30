<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("splashscreen")) {
            Schema::create("splashscreen", function (Blueprint $table) {
                $table->id();
                $table->string("name", 255);
                $table->enum("category", ["image", "font"]);
                $table->longText("svg_content");
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("category");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("splashscreen");
    }
};
