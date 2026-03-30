"""API DHT: Endpoints para descubrimiento de pares (Fase 9)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from servidor.dht.nodo import NodoDHT

router = APIRouter()
nodo_dht = NodoDHT()

class PublicarPeerRequest(BaseModel):
    peer_id: str
    endpoint: str
    firma: str
    ttl: int

class RenovarPeerRequest(BaseModel):
    peer_id: str
    firma: str
    ttl: int

@router.post("/v1/dht/publicar")
async def publicar_peer(req: PublicarPeerRequest):
    ok = nodo_dht.publicar_peer(req.peer_id, req.endpoint, req.firma, req.ttl)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo publicar el peer")
    return {"ok": True}

@router.get("/v1/dht/buscar/{peer_id}")
async def buscar_peer(peer_id: str):
    res = nodo_dht.buscar_peer(peer_id)
    if not res:
        raise HTTPException(status_code=404, detail="Peer no encontrado o expirado")
    return res

@router.post("/v1/dht/renovar")
async def renovar_peer(req: RenovarPeerRequest):
    ok = nodo_dht.renovar_peer(req.peer_id, req.firma, req.ttl)
    if not ok:
        raise HTTPException(status_code=400, detail="No se pudo renovar el peer (firma incorrecta o no existe)")
    return {"ok": True}
