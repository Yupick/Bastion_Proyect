import { useMemo, useState } from 'react'
import { adminUsers } from '../store/adminStore'

type UserStatus = 'activo' | 'bloqueado'

export function UsersPage() {
  const [localStatus, setLocalStatus] = useState<Record<string, UserStatus>>({})

  const users = useMemo(
    () =>
      adminUsers.map((user) => ({
        ...user,
        status: localStatus[user.id] ?? user.status,
      })),
    [localStatus],
  )

  const toggleStatus = (id: string, current: UserStatus) => {
    setLocalStatus((previous) => ({
      ...previous,
      [id]: current === 'activo' ? 'bloqueado' : 'activo',
    }))
  }

  return (
    <section className="card-page">
      <div className="card-head">
        <h2>Usuarios administrativos</h2>
        <p>Gestion base de acceso para roles admin, operador y analista.</p>
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Alias</th>
            <th>Rol</th>
            <th>Estado</th>
            <th>Ultima actividad</th>
            <th>Accion</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.alias}</td>
              <td>{user.role}</td>
              <td>
                <span className={`pill ${user.status === 'activo' ? 'pill-ok' : 'pill-danger'}`}>
                  {user.status}
                </span>
              </td>
              <td>{user.lastSeen}</td>
              <td>
                <button type="button" onClick={() => toggleStatus(user.id, user.status)}>
                  {user.status === 'activo' ? 'Bloquear' : 'Reactivar'}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  )
}
