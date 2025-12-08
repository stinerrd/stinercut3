<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('workload', function (Blueprint $table) {
            $table->binary('qr')->nullable()->after('uuid');
        });
    }

    public function down(): void
    {
        Schema::table('workload', function (Blueprint $table) {
            $table->dropColumn('qr');
        });
    }
};
