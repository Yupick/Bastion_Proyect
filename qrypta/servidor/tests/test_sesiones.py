from servidor.ws.sesiones import GestorSesiones

def test_crear_sesion_1a1():
    gestor = GestorSesiones()
    sesion = gestor.crear_sesion("1a1", ["alice", "bob"])
    assert sesion.tipo == "1a1"
    assert set(sesion.miembros) == {"alice", "bob"}
    assert sesion.es_valida()

def test_crear_sesion_grupo():
    gestor = GestorSesiones()
    sesion = gestor.crear_sesion("grupo", ["alice", "bob", "carol"])
    assert sesion.tipo == "grupo"
    assert len(sesion.miembros) == 3
    assert sesion.es_valida()

def test_expiracion():
    gestor = GestorSesiones()
    sesion = gestor.crear_sesion("1a1", ["a", "b"], ttl=1)
    import time
    time.sleep(2)
    assert not sesion.es_valida()
    gestor.limpiar_expiradas()
    assert sesion.id not in gestor.sesiones
