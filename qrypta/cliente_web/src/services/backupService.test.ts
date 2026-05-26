import { describe, expect, test } from 'vitest'
import { exportEncryptedBackup, importEncryptedBackup } from './backupService'

describe('backupService', () => {
  test('exporta e importa snapshot cifrado', async () => {
    const snapshot = {
      alias: 'operator-web',
      mnemonic: 'word '.repeat(24).trim(),
      deviceLinks: ['laptop', 'tablet'],
      exportedAt: new Date().toISOString(),
    }

    const blob = await exportEncryptedBackup(snapshot, 'passphrase-segura')
    const restored = await importEncryptedBackup(blob, 'passphrase-segura')

    expect(restored.alias).toBe(snapshot.alias)
    expect(restored.deviceLinks).toEqual(snapshot.deviceLinks)
  })

  test('falla con passphrase corta', async () => {
    await expect(
      exportEncryptedBackup(
        {
          alias: 'x',
          mnemonic: 'm',
          deviceLinks: [],
          exportedAt: new Date().toISOString(),
        },
        '1234',
      ),
    ).rejects.toThrow('Passphrase demasiado corta')
  })
})
