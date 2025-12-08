<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;
use WouterJ\EloquentBundle\Facade\Db;

return new class extends Migration
{
    public function up(): void
    {
        // Drop foreign key constraint from workload table first
        if (Schema::hasTable("workload")) {
            Schema::table("workload", function (Blueprint $table) {
                $table->dropForeign(["tandem_master_id"]);
                $table->dropIndex("idx_workload_tandem_master");
            });
        }

        // Rename tandem_master table to videographer
        if (Schema::hasTable("tandem_master")) {
            Schema::rename("tandem_master", "videographer");
        }

        // Rename column in workload table and recreate foreign key
        if (Schema::hasTable("workload")) {
            Schema::table("workload", function (Blueprint $table) {
                $table->renameColumn("tandem_master_id", "videographer_id");
            });

            Schema::table("workload", function (Blueprint $table) {
                $table->foreign("videographer_id")
                    ->references("id")
                    ->on("videographer")
                    ->nullOnDelete();
                $table->index("videographer_id", "idx_workload_videographer");
            });
        }
    }

    public function down(): void
    {
        // Drop foreign key constraint from workload table first
        if (Schema::hasTable("workload")) {
            Schema::table("workload", function (Blueprint $table) {
                $table->dropForeign(["videographer_id"]);
                $table->dropIndex("idx_workload_videographer");
            });
        }

        // Rename videographer table back to tandem_master
        if (Schema::hasTable("videographer")) {
            Schema::rename("videographer", "tandem_master");
        }

        // Rename column back in workload table and recreate foreign key
        if (Schema::hasTable("workload")) {
            Schema::table("workload", function (Blueprint $table) {
                $table->renameColumn("videographer_id", "tandem_master_id");
            });

            Schema::table("workload", function (Blueprint $table) {
                $table->foreign("tandem_master_id")
                    ->references("id")
                    ->on("tandem_master")
                    ->nullOnDelete();
                $table->index("tandem_master_id", "idx_workload_tandem_master");
            });
        }
    }
};
