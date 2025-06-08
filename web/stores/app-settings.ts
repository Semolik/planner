import { defineStore } from "pinia";
import {
    SettingsService,
    type Settings,
    type EventLevelRead,
    EventsLevelsService,
} from "@/client";
export const useAppSettingsStore = defineStore("app-settings", {
    state: () => ({
        settings: null as Settings | null,
        eventsLevels: [] as EventLevelRead[],
    }),
    actions: {
        async getSettings() {
            this.settings = await SettingsService.getSettingsSettingsGet();
            this.eventsLevels =
                await EventsLevelsService.getEventLevelsEventsLevelsGet();
        },
    },
});
