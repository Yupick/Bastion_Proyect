## Arquitectura del Sistema

- Cliente A
  - Clave pública/privada Kyber + Dilithium
  - Alias opcional firmado
  - Lista local de contactos

- Servidor de Enrutamiento
  - No guarda contenido ni identidades
  - Enruta por ID de clave pública

- Cliente B
  - Verifica firma con clave pública
  - Recibe mensaje cifrado

- Auditoría Pública
  - Código abierto
  - Logs verificables
  - Reportes de transparencia
