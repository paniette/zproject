import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import { renameSync, copyFileSync, existsSync, mkdirSync, readdirSync, statSync } from 'fs'
import { resolve, join } from 'path'

// Plugin pour copier les fichiers du build à la racine et renommer index.html en editor.html
const copyAndRenamePlugin = () => {
  return {
    name: 'copy-and-rename',
    closeBundle() {
      const distDir = resolve(__dirname, 'dist')
      const rootDir = resolve(__dirname, '..')
      
      if (!existsSync(distDir)) {
        console.warn('Build directory not found')
        return
      }
      
      // Fonction récursive pour copier les fichiers
      const copyRecursive = (src, dest) => {
        const stats = statSync(src)
        if (stats.isDirectory()) {
          if (!existsSync(dest)) {
            mkdirSync(dest, { recursive: true })
          }
          const files = readdirSync(src)
          for (const file of files) {
            copyRecursive(join(src, file), join(dest, file))
          }
        } else {
          copyFileSync(src, dest)
        }
      }
      
      // Copier tous les fichiers du dist à la racine
      const files = readdirSync(distDir)
      for (const file of files) {
        const src = join(distDir, file)
        const dest = join(rootDir, file)
        
        if (file === 'index.html') {
          // Renommer index.html en editor.html
          copyFileSync(src, join(rootDir, 'editor.html'))
          console.log('✓ Created editor.html')
        } else {
          // Copier les autres fichiers (assets/, packs-index.json, etc.)
          const stats = statSync(src)
          if (stats.isDirectory()) {
            copyRecursive(src, dest)
          } else {
            copyFileSync(src, dest)
          }
        }
      }
      
      console.log('✓ Build files copied to root directory')
    }
  }
}

export default defineConfig({
  base: './',  // Chemins relatifs pour que tout fonctionne à la racine
  plugins: [vue(), copyAndRenamePlugin()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // Copy packs-index.json to dist
  publicDir: 'public',
  build: {
    outDir: 'dist',  // Build dans frontend/dist temporairement
    emptyOutDir: true
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/bgmapeditor_tiles': {
        target: 'http://localhost:8000',
        changeOrigin: true
      },
      '/assets': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
