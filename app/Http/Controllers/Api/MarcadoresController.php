<?php

namespace App\Http\Controllers\Api;


use App\Http\Controllers\Controller;
use App\Models\marcadores;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Symfony\Component\Process\Process;
use Symfony\Component\Process\Exception\ProcessFailedException;

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
        $apiKey = config('services.google_maps.api_key');
        $radius = 10000; // Reducimos el radio para hacer más búsquedas
        $maxRequests = 5; // Número de zonas en Cali a consultar
    
        if (!$apiKey) {
            return response()->json(['error' => 'API Key no encontrada'], 500);
        }
    
        $tipo = strtolower($tipo);
        $tipo = rtrim($tipo, 's');
    
        $mapaTipos = [
            'hospital' => ['type' => 'hospital', 'keyword' => 'hospital'],
            'school' => ['type' => 'school', 'keyword' => 'colegio'],
            'hotel' => ['type' => 'lodging', 'keyword' => 'hotel'],
            'banco' => ['type' => 'bank', 'keyword' => 'banco'],
            'cajero' => ['type' => 'atm', 'keyword' => 'cajero'],
            'plaza' => ['type' => 'park', 'keyword' => 'plaza'],
        ];
    
        if (!isset($mapaTipos[$tipo])) {
            return response()->json(['error' => 'Tipo de lugar no válido'], 400);
        }
    
        // Coordenadas estratégicas en Cali para aumentar la cobertura
        $locations = [
            '3.4516,-76.5320', // Centro de Cali
            '3.4300,-76.5400', // Norte de Cali
            '3.4700,-76.5200', // Sur de Cali
            '3.4500,-76.5500', // Oeste de Cali
            '3.4300,-76.5100', // Este de Cali
        ];
    
        $uniqueResults = [];
    
        foreach ($locations as $location) {
            $params = [
                'location' => $location,
                'radius' => $radius,
                'type' => $mapaTipos[$tipo]['type'],
                'keyword' => $mapaTipos[$tipo]['keyword'],
                'language' => 'es',
                'key' => $apiKey
            ];
    
            $nextPageToken = null;
            $attempts = 0;
    
            do {
                if ($nextPageToken) {
                    $params['pagetoken'] = $nextPageToken;
                    sleep(2); // Google recomienda esperar antes de hacer una petición con nextPageToken
                }
    
                $response = Http::get("https://maps.googleapis.com/maps/api/place/nearbysearch/json", $params);
                $data = $response->json();
    
                if (isset($data['results'])) {
                    foreach ($data['results'] as $result) {
                        // Usamos place_id como clave para evitar duplicados
                        $uniqueResults[$result['place_id']] = $result;
                    }
                }
    
                $nextPageToken = $data['next_page_token'] ?? null;
                $attempts++;
    
            } while ($nextPageToken && $attempts < 3); // Hasta 3 páginas por coordenada
        }
    
        return response()->json(array_values($uniqueResults)); // Convertir de nuevo a array indexado
    }
    


    public function procesarProyeccionesCali(Request $request)
{
    try {
        // Validar archivo
        if (!$request->hasFile('archivo')) {
            return response()->json(['error' => 'No se encontró ningún archivo'], 400);
        }

        // Guardar el archivo
        $archivo = $request->file('archivo');
        $rutaArchivo = storage_path('app/homicidios_cali.xlsx'); // Sin "public/"
        $archivo->move(storage_path('app'), 'homicidios_cali.xlsx');

        // Ruta al script de Python
        $rutaScript = base_path('app/Http/Controllers/Api/proyecciones.py');

        // Ruta al ejecutable de Python
        $pythonPath = '"C:\xampp\htdocs\tesisbackend\node_modules\python"'; // Ajusta según el resultado de `where python`

        // Ejecutar script
        $process = new Process([$pythonPath, $rutaScript, $rutaArchivo]);
        $process->run();

        // Verificar errores
        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }

        // Obtener salida
        $salida = json_decode($process->getOutput(), true);

        return response()->json($salida);
    } catch (\Exception $e) {
        return response()->json(['error' => 'Excepción en PHP: ' . $e->getMessage()], 500);
    }
}
    


    
}
