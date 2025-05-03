import { defineStore } from "pinia";
import { SettingsService } from "@/client";
export const useAppSettingsStore = defineStore("app-settings", {
    state: async () => {
        const settings = await SettingsService.getSettingsSettingsGet();
        return settings;
    },
});
