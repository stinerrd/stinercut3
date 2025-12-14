<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use WouterJ\EloquentBundle\Facade\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable("video_file_segment")) {
            Schema::create("video_file_segment", function (Blueprint $table) {
                $table->id();
                $table->string("uuid", 36)->unique();
                $table->bigInteger("video_file_id")->unsigned();

                // Timeslot
                $table->decimal("start_time", 10, 3);
                $table->decimal("end_time", 10, 3);

                // Classification: qr_code, ground_before, flight, freefall, canopy, ground_after, unknown
                $table->string("classification", 50);
                $table->decimal("confidence", 5, 4)->nullable();

                // Order within video
                $table->integer("sequence_order");

                $table->dateTime("created_at");

                $table->charset = "utf8mb4";
                $table->collation = "utf8mb4_unicode_ci";
                $table->engine = "InnoDB";

                $table->foreign("video_file_id")
                    ->references("id")
                    ->on("video_file")
                    ->onDelete("cascade");

                $table->index("video_file_id");
                $table->index("classification");
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists("video_file_segment");
    }
};
