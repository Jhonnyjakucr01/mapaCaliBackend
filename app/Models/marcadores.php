<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class marcadores extends Model
{
    use HasFactory;
    protected $fillable = ['tipo','nombre','latitud', 'longitud'];

}
