<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table("workload", function (Blueprint $table) {
            $table->string("type", 50)->default("tandem_hc")->after("videographer_id");
            $table->index("type", "idx_workload_type");
        });
    }

    public function down(): void
    {
        Schema::table("workload", function (Blueprint $table) {
            $table->dropIndex("idx_workload_type");
            $table->dropColumn("type");
        });
    }
};
