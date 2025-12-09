<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table("videopart", function (Blueprint $table) {
            $table->integer("duration")->nullable()->unsigned()->after("thumbnail");
        });
    }

    public function down(): void
    {
        Schema::table("videopart", function (Blueprint $table) {
            $table->dropColumn("duration");
        });
    }
};
