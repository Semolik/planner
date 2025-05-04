import { defineStore } from "pinia";
import { SettingsService, type Settings } from "@/client";
export const useAppSettingsStore = defineStore("app-settings", {
    state: () => ({
        settings: null as Settings | null,
    }),
    actions: {
        async getSettings() {
            this.settings = await SettingsService.getSettingsSettingsGet();
        },
    },
});
