<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('client', function (Blueprint $table) {
            $table->id();
            $table->string('name', 255);
            $table->string('email', 255)->nullable();
            $table->string('phone', 50)->nullable();
            $table->boolean('marketing_flag')->default(false);
            $table->timestamps();

            $table->index('name', 'idx_client_name');
            $table->index('marketing_flag', 'idx_client_marketing_flag');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('client');
    }
};
