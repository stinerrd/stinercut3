<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table("import_batch", function (Blueprint $table) {
            $table->string("mount_path", 255)->nullable()->after("error_message");
        });
    }

    public function down(): void
    {
        Schema::table("import_batch", function (Blueprint $table) {
            $table->dropColumn("mount_path");
        });
    }
};
