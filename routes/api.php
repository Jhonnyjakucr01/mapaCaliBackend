<?php

use App\Http\Controllers\Api\marcadoresController;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "api" middleware group. Make something great!
|
*/
Route::post('users/{id}', function ($id) {
    
});

Route::group(['middleware' => 'cors'], function () {


    Route::apiResource('marcadores', MarcadoresController::class);
    Route::get('icono-por-categoria/{categoria}', [MarcadoresController::class, 'getIconByCategory']);
    Route::get('obtener-datos-google/{tipo}', [MarcadoresController::class, 'obtenerDatosGoogle']);


    
});