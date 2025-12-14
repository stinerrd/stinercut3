<?php

use Illuminate\Database\Migrations\Migration;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // Rename tandem_master table to videographer
        if (Schema::hasTable("tandem_master")) {
            Schema::rename("tandem_master", "videographer");
        }
    }

    public function down(): void
    {
        // Rename videographer table back to tandem_master
        if (Schema::hasTable("videographer")) {
            Schema::rename("videographer", "tandem_master");
        }
    }
};
