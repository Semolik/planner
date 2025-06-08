<template>
    <app-form full-height headline="Создание мероприятия">
        <app-input v-model="name" label="Название мероприятия" required white />
        <app-input
            v-model="date"
            type="date"
            label="Дата мероприятия"
            required
            white
        />
        <div class="flex gap-1">
            <app-input
                v-model="timeStart"
                type="time"
                label="Время начала"
                required
                white
            />
            <app-input
                v-model="timeEnd"
                type="time"
                label="Время окончания"
                required
                white
            />
        </div>
        <app-input v-model="location" label="Место проведения" required white />
        <app-input
            v-model="organizer"
            label="Контакт организатора"
            required
            white
        />

        <div class="flex flex-col gap-1 w-full">
            <div class="event-form-label">Уровень мероприятия</div>
            <client-only>
                <USelectMenu
                    v-model="event_level"
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
            </client-only>
        </div>
        <app-button :active="buttonActive" @click="createEvent">
            Создать мероприятие
        </app-button>
    </app-form>
</template>
<script setup>
import { useAppSettingsStore } from "~/stores/app-settings";
import { EventsService } from "~/client";
import { routesNames } from "@typed-router";
const appSettingsStore = useAppSettingsStore();
definePageMeta({
    middleware: ["admin"],
});
const name = ref("");
const date = ref("");
const timeStart = ref("");
const timeEnd = ref("");
const currentDate = ref(new Date().toISOString().slice(0, 10));
const location = ref("");
const organizer = ref("");

const eventLevels = appSettingsStore.eventsLevels.map((level) => ({
    id: level.id,
    label: level.name,
}));
const event_level = ref(
    eventLevels.find(
        (level) => level.id === appSettingsStore.settings.default_event_level_id
    )
);
const buttonActive = computed(() => {
    return (
        name.value.length > 0 &&
        date.value.length > 0 &&
        timeStart.value.length > 0 &&
        timeEnd.value.length > 0 &&
        location.value.length > 0 &&
        event_level.value !== null
    );
});
watch(timeStart, (value) => {
    if (
        new Date(`${currentDate.value}T${value}`) >=
        new Date(`${currentDate.value}T${timeEnd.value}`)
    ) {
        const endTime = new Date(`${currentDate.value}T${value}`);
        if (endTime.getHours() < 23) {
            endTime.setHours(endTime.getHours() + 1);
        } else {
            endTime.setHours(0);
        }
        timeEnd.value = endTime.toTimeString().slice(0, 5);
    }
});
watch(timeEnd, (value) => {
    if (
        new Date(`${currentDate.value}T${value}`) <=
        new Date(`${currentDate.value}T${timeStart.value}`)
    ) {
        const startTime = new Date(`${currentDate.value}T${value}`);
        if (startTime.getHours() > 0) {
            startTime.setHours(startTime.getHours() - 1);
        } else {
            startTime.setHours(23);
        }
        timeStart.value = startTime.toTimeString().slice(0, 5);
    }
});
const { $toast } = useNuxtApp();
const createEvent = async () => {
    if (!buttonActive.value) return;
    try {
        const event = await EventsService.createEventEventsPost({
            name: name.value,
            date: date.value,
            start_time: `${timeStart.value}:00Z`,
            end_time: `${timeEnd.value}:00Z`,
            name_approved: false,
            location: location.value,
            link: "",
            organizer: organizer.value,
            required_photographers: 1,
            group_id: null,
            description: "",
            level_id: event_level.value.id,
            photographer_description: "",
            copywriter_description: "",
            designer_description: "",
            days_to_complete_photographers: 1,
            days_to_complete_copywriters: 1,
            days_to_complete_designers: 1,
        });
        const router = useRouter();
        $toast.success("Мероприятие успешно создано");
        router.push({
            name: routesNames.eventsEventId,
            params: { eventId: event.id },
        });
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    }
};
</script>
<style lang="scss">
.select-menu {
    --ui-border-accented: transparent !important;
}
</style>
<style scoped lang="scss">
.event-form-label {
    font-size: 14px;
    color: $text-color;
    text-decoration: none;
    margin-left: 3px;
}
</style>
