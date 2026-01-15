/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BACKEND_STATE_A_URL: string
  readonly VITE_BACKEND_STATE_B_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}