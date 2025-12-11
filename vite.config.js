import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
    build: {
        // Output to the WordPress theme assets folder
        outDir: 'yourparty-tech/assets/dist',
        emptyOutDir: true,
        manifest: true,
        rollupOptions: {
            input: {
                main: path.resolve(__dirname, 'src/js/main.js')
            },
            output: {
                entryFileNames: `[name].js`,
                chunkFileNames: `[name].js`,
                assetFileNames: `[name].[ext]`
            }
        }
    },
    server: {
        // Proxy configuration could go here if we wanted to proxy WP
        port: 3000
    }
});
