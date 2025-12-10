<template>
    <UModal
        :open="open"
        @update:open="emit('update:open', $event)"
        title="Удаление отчетного периода"
        v-if="period"
        class="max-w-md"
    >
        <template #body>
            <div class="flex flex-col gap-4">
                <p class="text-gray-700">
                    Вы уверены, что хотите удалить отчетный период
                    <span class="font-bold italic ">
                        {{ formatPeriod(period) }}
                    </span>? Это действие нельзя будет отменить.
                </p>

                <div class="grid grid-cols-2 gap-3 pt-2">
                    <app-button
                        active
                        @click="emit('update:open', false)"
                        :disabled="isLoading"
                        class="cursor-pointer"
                    >
                        Отмена
                    </app-button>
                    <app-button
                        active
                        red
                        :loading="isLoading"
                        @click="confirmDelete"
                    >
                        Удалить период
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>
</template>

<script setup lang="ts">
import { RequiredPeriodsService } from "~/client";
import type { RequiredPeriod } from "~/client";
import { ref } from 'vue';

const props = defineProps<{
    period: RequiredPeriod | null;
    open: boolean;
}>();

const emit = defineEmits<{
    (e: "update:open", value: boolean): void;
    (e: "deleted"): void;
}>();

const isLoading = ref(false);
const { $toast } = useNuxtApp();

// Форматирование периода для отображения
const formatPeriod = (period: RequiredPeriod): string => {
    const start = new Date(period.period_start).toLocaleDateString("ru-RU");
    const end = new Date(period.period_end).toLocaleDateString("ru-RU");

    if (start === end) {
        return `${start}`;
    }

    return `${start} - ${end}`;
};

// Подтверждение удаления
const confirmDelete = async () => {
    if (!props.period) return;

    try {
        isLoading.value = true;

        await RequiredPeriodsService.deleteRequiredPeriodRequiredPeriodsPeriodIdDelete(
            props.period.id
        );

        $toast.success("Отчетный период успешно удален");
        emit("deleted");
        emit("update:open", false);
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
};
</script>
