import { expect, test } from '@playwright/test'

test('muestra shell principal y estado cifrado', async ({ page }) => {
  await page.goto('/')
  await expect(page.getByText('Mensajeria Segura')).toBeVisible()
  await expect(page.getByText('Canal cifrado')).toBeVisible()
})

test('abre sección de ajustes', async ({ page }) => {
  await page.goto('/')
  await page.getByRole('button', { name: 'Ajustes' }).click()
  await expect(page.getByText('Config panel')).toBeVisible()
})
