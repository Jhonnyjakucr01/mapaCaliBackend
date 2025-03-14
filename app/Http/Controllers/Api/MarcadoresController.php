<?php

namespace App\Http\Controllers\Api;


use App\Http\Controllers\Controller;
use App\Models\marcadores;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class MarcadoresController extends Controller
{
    public function index()
    {
        try {
            $marcadores = marcadores::get();

            return response()->json([
                'status' => 'success',
                'data' => $marcadores,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => $e->getMessage(),
                'line' => $e->getLine(),
            ], 500);
        }
    }


    public function getIconByCategory(string $category): string
    {
        $category = strtolower($category);  // Convertir la categoría a minúsculas

        switch ($category) {
            case "hospitales":
                return "/Icons/marcadorAmarillo.png";
            case "colegios":
                return "/Icons/marcadorAzul.png";
            case "clinicas":
                return "/Icons/marcadorBlanca.png";
            case "bancos":
                return "/Icons/marcadorDorado.png";
            case "universidades":
                return "/Icons/marcadorRosa.png";
            case "centros comerciales":
                return "/Icons/marcadorNaranja.png";
            case "monumentos":
                return "/Icons/marcadorMorado.png";
            case "fotomultas":
                return "/Icons/marcadorVerde.png";
            case "comunas":
                return "/Icons/marcadorNegro.png";
            case "hoteles":
                return "/Icons/marcadorRojo.png";
            default:
                return "/Icons/marcadorCafe.png"; // Valor por defecto
        }
    }




    public function store(Request $request)
    {
        $request->validate([
            'nombre' => 'required|string|max:100',
            'tipo' => 'required|string|max:100',
            'lat' => 'required|numeric',
            'lng' => 'required|numeric',
        ]);
    
        try {
            // Extraer y convertir lat y lng a string
            $latitud = (string) $request->lat;
            $longitud = (string) $request->lng;
    
            // Crear la instancia del marcador
            $marcador = new marcadores();
            $marcador->nombre = $request->nombre;
            $marcador->tipo = $request->tipo;
            $marcador->latitud = $latitud; // Insertar como string
            $marcador->longitud = $longitud; // Insertar como string
    
            $marcador->save();
    
            return response()->json([
                'status' => 'success',
                'data' => $marcador,
            ], 201);
        } catch (\Exception $e) {
            return response()->json([
                'status' => 'error',
                'message' => $e->getMessage(),
                'line' => $e->getLine(),
            ], 500);
        }
    }


    public function obtenerDatosGoogle($tipo)
{
    $apiKey = config('services.google_maps.api_key'); // Obtener la clave desde el config
    $location = '3.4516,-76.5320'; // Coordenadas de Cali
    $radius = 25000; // Aumenté el radio de búsqueda a 25 km

    if (!$apiKey) {
        return response()->json(['error' => 'API Key no encontrada'], 500);
    }

    // Mapeo de términos en español a palabras clave en inglés y búsqueda por keyword
    $mapaTipos = [
        'hospital' => ['type' => 'hospital', 'keyword' => 'hospital'],
        'colegios' => ['type' => 'school', 'keyword' => 'colegio'],
        'hoteles' => ['type' => 'lodging', 'keyword' => 'hotel'],
        'bancos' => ['type' => 'bank', 'keyword' => 'banco'],
        'cajeros' => ['type' => 'atm', 'keyword' => 'cajero'],
        'plazas' => ['type' => 'park', 'keyword' => 'plaza'],
    ];

    if (!isset($mapaTipos[$tipo])) {
        return response()->json(['error' => 'Tipo de lugar no válido'], 400);
    }

    $params = [
        'location' => $location,
        'radius' => $radius,
        'type' => $mapaTipos[$tipo]['type'],
        'keyword' => $mapaTipos[$tipo]['keyword'], // Se usa keyword para mejorar la búsqueda
        'language' => 'es', // Resultados en español
        'key' => $apiKey
    ];

    $response = Http::get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", $params);

    return response()->json($response->json());
}




    
}
