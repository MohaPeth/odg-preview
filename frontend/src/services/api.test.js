/**
 * Tests du service API WebGIS.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import ApiService from './api.js'

describe('ApiService', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('getLayers appelle fetch avec la bonne URL', async () => {
    const mockJson = vi.fn().mockResolvedValue({ success: true, data: [] })
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: mockJson,
    })

    await ApiService.getLayers()

    expect(fetch).toHaveBeenCalledWith(
      '/api/webgis/layers',
      expect.objectContaining({
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      })
    )
  })

  it('getDeposits appelle fetch avec /api/webgis/deposits', async () => {
    const mockJson = vi.fn().mockResolvedValue({ success: true, data: [], count: 0 })
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: mockJson,
    })

    await ApiService.getDeposits({})

    expect(fetch).toHaveBeenCalledWith(
      '/api/webgis/deposits',
      expect.objectContaining({
        method: 'GET',
      })
    )
  })
})
