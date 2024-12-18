<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('marcadores', function (Blueprint $table) {
            $table->id();
            $table->string('tipo', 35);
            $table->string('nombre', 80);
            $table->string('latitud', 35);
            $table->string('longitud', 35);
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('marcadores');
    }
};
