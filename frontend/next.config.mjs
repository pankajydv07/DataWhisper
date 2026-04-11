import { existsSync, readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const frontendDir = dirname(fileURLToPath(import.meta.url))
const rootEnvPath = resolve(frontendDir, "..", ".env")

if (existsSync(rootEnvPath)) {
  const lines = readFileSync(rootEnvPath, "utf-8").split(/\r?\n/)
  for (const line of lines) {
    const match = line.match(/^\s*([^#][^=]+)=(.*)$/)
    if (match) {
      const key = match[1].trim()
      const value = match[2].trim()
      process.env[key] ??= value
    }
  }
}

/** @type {import('next').NextConfig} */
const nextConfig = {}

export default nextConfig
