/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_MAPBOX_TOKEN: string
  readonly VITE_MODE: 'MOCK' | 'LIVE'
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
