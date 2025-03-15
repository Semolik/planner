// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2024-11-01",
    devtools: { enabled: true },
    css: ["@/styles/global.scss"],

    vite: {
        css: {
            preprocessorOptions: {
                scss: {
                    additionalData: [
                        '@use "@/styles/_colors.scss" as *;',
                        '@use "@/styles/helpers.scss" as *;',
                        '@use "@/styles/breakpoints.scss" as *;',
                    ].join(""),
                    silenceDeprecations: [
                        "mixed-decls",
                        "color-functions",
                        "global-builtin",
                        "import",
                    ],
                },
            },
        },
    },

    modules: [[
        "@nuxtjs/google-fonts",
        {
            families: {
                "Open Sans": true,
            },

            display: "swap",
        },
    ], "@pinia/nuxt"],
});