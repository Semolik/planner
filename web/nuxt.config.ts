// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2024-11-01",
    devtools: { enabled: true },

    modules: [
        "@pinia/nuxt",
        "@nuxtjs/google-fonts",
        "@nuxt/icon",
        "@formkit/auto-animate/nuxt",
        "@vueuse/nuxt",
        "@nuxt/ui",
        "nuxt-typed-router",
        "nuxt-viewport",
    ],
    ui: {
        colorMode: false,
    },
    viewport: {
        breakpoints: {
            xs: 360,
            sm: 576,
            md: 768,
            lg: 992,
            xl: 1200,
            xxl: 1400,
        },
    },
    icon: {
        provider: "server",
        localApiEndpoint: "/icons-api",
        serverBundle: {
            collections: ["material-symbols", "mdi"],
        },
    },
    googleFonts: {
        families: {
            Inter: [400, 600, 700, 800],
        },
        download: true,
    },
    vite: {
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: [
                        '@use "@/styles/_colors.scss" as *;',
                        '@use "@/styles/helpers.scss" as *;',
                        '@use "@/styles/breakpoints.scss" as *;',
                    ].join(""),
                },
            },
        },
    },
    css: ["@/styles/global.scss", "@/styles/main.css"],
    routeRules: {
        "/api/**": {
            proxy: {
                to:
                    process.env.NODE_ENV === "development"
                        ? "http://localhost:8000/**"
                        : "http://api:8000/**",
            },
        },
    },
});
