import { expect, test } from '@playwright/test'

test('muestra login admin', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Ingreso administrativo')).toBeVisible()
})

test('permite entrar con TOTP demo', async ({ page }) => {
  await page.goto('/')
  await page.getByPlaceholder('123456').fill('123456')
  await page.getByRole('button', { name: 'Validar sesión' }).click()
  await expect(page.getByText('Centro de Control')).toBeVisible()
})
