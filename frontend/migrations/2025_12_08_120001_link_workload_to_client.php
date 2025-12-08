<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('workload', function (Blueprint $table) {
            // Add client_id column
            $table->unsignedBigInteger('client_id')->nullable()->after('id');
            $table->foreign('client_id')
                ->references('id')
                ->on('client')
                ->onDelete('set null');
            $table->index('client_id', 'idx_workload_client_id');

            // Remove old columns
            $table->dropColumn(['name', 'email', 'phone', 'marketing_flag']);
        });
    }

    public function down(): void
    {
        Schema::table('workload', function (Blueprint $table) {
            // Restore old columns
            $table->string('name', 255)->nullable()->after('qr');
            $table->string('email', 255)->nullable()->after('name');
            $table->string('phone', 50)->nullable()->after('email');
            $table->boolean('marketing_flag')->default(false)->after('photo');

            // Remove client_id column
            $table->dropForeign(['client_id']);
            $table->dropIndex('idx_workload_client_id');
            $table->dropColumn('client_id');
        });
    }
};
