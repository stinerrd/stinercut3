<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("videopart")) {
            Schema::create("videopart", function (Blueprint $table) {
                $table->id();
                $table->string("name", 255);
                $table->string("type", 50);  // 'intro' or 'outro'
                $table->text("description")->nullable();
                $table->string("file_path", 500);
                $table->binary("thumbnail")->nullable();  // LONGBLOB for thumbnail
                $table->timestamps();

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->index("type");
                $table->index("name");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("videopart");
    }
};
