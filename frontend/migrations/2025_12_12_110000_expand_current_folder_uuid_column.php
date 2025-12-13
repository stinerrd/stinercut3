<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table("video_file", function (Blueprint $table) {
            // Expand to support CLIENT_NAME_UUID format (e.g., "Test_Client_c0abffcf-029d-4c81-87b8-839952125d4f")
            $table->string("current_folder_uuid", 255)->change();
        });
    }

    public function down(): void
    {
        Schema::table("video_file", function (Blueprint $table) {
            $table->string("current_folder_uuid", 36)->change();
        });
    }
};
