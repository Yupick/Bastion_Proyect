import { useMemo } from 'react'

export function useContacts() {
  const contacts = useMemo(
    () => [
      {
        id: 'c1',
        nombre: 'Nodo Aurora',
        ultimoMensaje: 'Confirmado. Handshake dilithium validado.',
        hora: '11:42',
        noLeidos: 2,
        estado: 'online' as const,
      },
      {
        id: 'c2',
        nombre: 'Equipo Admin',
        ultimoMensaje: 'La auditoria diaria quedo publicada.',
        hora: '10:09',
        noLeidos: 0,
        estado: 'online' as const,
      },
      {
        id: 'c3',
        nombre: 'Laboratorio PQC',
        ultimoMensaje: 'Nuevo set de claves listo para rotacion.',
        hora: 'Ayer',
        noLeidos: 1,
        estado: 'offline' as const,
      },
    ],
    [],
  )

  return {
    contacts,
  }
}
