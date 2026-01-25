<template>
    <app-form full-height headline="Настройки">

        <app-input
            v-model="appName"
            label="Название приложения"
            required
            white
            :min="1"
        />
        <app-input
            v-model="photographersDeadline"
            label="Дней на обработку репортажа"
            type="number"
            required
            white
            :min="1"
        />
        <app-input
            v-model="copywritersDeadline"
            label="Дней на написание поста к репортажу"
            type="number"
            required
            white
            :min="1"
        />
        <app-input
            v-model="designersDeadline"
            label="Дней после обработки репортажа на дизайн"
            type="number"
            required
            white
            :min="1"
        />
        <div class="flex flex-col gap-1 w-full">
            <div class="event-form-label">Уровень мероприятия по умолчанию</div>

            <USelectMenu
                v-model="defaultEventLevel"
                :items="eventLevels"
                class="select-menu"
                color="neutral"
                size="lg"
                :content="{
                    align: 'start',
                    side: 'bottom',
                    sideOffset: 8,
                }"
                :search-input="{
                    placeholder: 'Поиск',
                }"
            />
        </div>
        <app-button :active="saveButtonActive" @click="saveSettings">
            Сохранить
        </app-button>
    </app-form>
</template>
<script setup>
import { useAppSettingsStore } from "~/stores/app-settings";
import { SettingsService } from "@/client";
definePageMeta({
    middleware: ["admin"],
});
useSeoMeta({
    title: "Настройки приложения",
});
const appSettingsStore = useAppSettingsStore();
await appSettingsStore.getSettings();
const appName = ref(appSettingsStore.settings.app_name);
const photographersDeadline = ref(
    appSettingsStore.settings.photographers_deadline
);
const copywritersDeadline = ref(appSettingsStore.settings.copywriters_deadline);
const designersDeadline = ref(appSettingsStore.settings.designers_deadline);
const eventLevels = appSettingsStore.eventsLevels.map((level) => ({
    id: level.id,
    label: level.name,
}));
const defaultEventLevel = ref(
    eventLevels.find(
        (level) => level.id === appSettingsStore.settings.default_event_level_id
    )
);
const saveButtonActive = computed(() => {
    return (
        appName.value.length > 0 &&
        photographersDeadline.value > 0 &&
        copywritersDeadline.value > 0 &&
        designersDeadline.value > 0 &&
        defaultEventLevel.value !== null &&
        (appName.value !== appSettingsStore.settings.app_name ||
            photographersDeadline.value !==
                appSettingsStore.settings.photographers_deadline ||
            copywritersDeadline.value !==
                appSettingsStore.settings.copywriters_deadline ||
            designersDeadline.value !==
                appSettingsStore.settings.designers_deadline ||
            defaultEventLevel.value.id !==
                appSettingsStore.settings.default_event_level_id)
    );
});
const { $toast } = useNuxtApp();
const saveSettings = async () => {
    if (!saveButtonActive.value) return;
    try {
        appSettingsStore.settings =
            await SettingsService.updateSettingSettingsPut({
                app_name: appName.value,
                photographers_deadline: photographersDeadline.value,
                copywriters_deadline: copywritersDeadline.value,
                designers_deadline: designersDeadline.value,
                default_event_level_id: defaultEventLevel.value.id,
            });
    } catch (error) {
        console.error("Ошибка при сохранении настроек:", error);
        $toast.error(HandleOpenApiError(error).message);
    }
};
</script>
