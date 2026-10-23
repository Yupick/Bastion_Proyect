"""API DHT: Endpoints para descubrimiento de pares (Fase 9)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from servidor.dht.nodo import NodoDHT

router = APIRouter()
nodo_dht = NodoDHT()

class PublicarPeerRequest(BaseModel):
    peer_id: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    endpoint: str = Field(min_length=1, max_length=256)
    firma: str = Field(min_length=1)
    ttl: int = Field(gt=0, le=86400)
    pubkey_dilithium_b64: str = Field(min_length=1)

class RenovarPeerRequest(BaseModel):
    peer_id: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    firma: str = Field(min_length=1)
    ttl: int = Field(gt=0, le=86400)

@router.post("/v1/dht/publicar")
async def publicar_peer(req: PublicarPeerRequest):
    ok = nodo_dht.publicar_peer(req.peer_id, req.endpoint, req.firma, req.ttl, req.pubkey_dilithium_b64)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo publicar el peer (firma invalida o peer_id no coincide con clave publica)")
    return {"ok": True}

@router.get("/v1/dht/buscar/{peer_id}")
async def buscar_peer(peer_id: str):
    res = nodo_dht.buscar_peer(peer_id)
    if not res:
        raise HTTPException(status_code=404, detail="Peer no encontrado o expirado")
    return res

@router.get("/v1/dht/pubkey/{peer_id}")
async def obtener_pubkey(peer_id: str):
    pubkey = nodo_dht.obtener_clave_publica(peer_id)
    if not pubkey:
        raise HTTPException(status_code=404, detail="Peer no encontrado o sin clave publica")
    return {"peer_id": peer_id, "pubkey_dilithium_b64": pubkey}

@router.post("/v1/dht/renovar")
async def renovar_peer(req: RenovarPeerRequest):
    ok = nodo_dht.renovar_peer(req.peer_id, req.firma, req.ttl)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo renovar el peer (firma incorrecta o no existe)")
    return {"ok": True}
