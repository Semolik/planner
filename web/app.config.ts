export default defineAppConfig({
    ui: {
        colors: {
            primary: "black",
            neutral: "slate",
        },
        modal: {
            slots: {
                body: "flex-1 overflow-y-auto p-4 sm:p-4",
                overlay: "fixed inset-0 bg-black/35",
            },
            variants: {
                fullscreen: {
                    false: {
                        content:
                            "top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[calc(100vw-2rem)] max-w-lg max-h-[calc(80dvh-2rem)] sm:max-h-[calc(80dvh-4rem)] rounded-lg shadow-lg ring ring-(--ui-border) max-w-[400px]",
                    },
                },
            },
        },
    },
});
