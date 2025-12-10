<template>
    <UModal
        :open="open"
        @update:open="$emit('update:open', $event)"
        :title="period ? 'Редактирование периода' : 'Создание периода'"
        class="max-w-2xl"
    >
        <template #body>
            <div class="flex flex-col gap-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <app-input
                        ref="startDateInput"
                        v-model="form.period_start"
                        label="Дата начала *"
                        type="date"
                        required
                        white
                        :validator="validationState.start"
                    />
                    <app-input
                        ref="endDateInput"
                        v-model="form.period_end"
                        label="Дата окончания *"
                        type="date"
                        required
                        white
                        :validator="validationState.end"
                    />
                </div>

                <!-- Остальные поля без изменений -->
                <div class="flex flex-col gap-2">
                    <div class="text-sm font-medium text-gray-700">Минимальное количество задач</div>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pl-2">
                        <app-input
                            v-model.number="form.photographers_count"
                            label="Фотографы"
                            type="number"
                            :min="0"
                            required
                            white
                        />
                        <app-input
                            v-model.number="form.copywriters_count"
                            label="Копирайтеры"
                            type="number"
                            :min="0"
                            required
                            white
                        />
                        <app-input
                            v-model.number="form.designers_count"
                            label="Дизайнеры"
                            type="number"
                            :min="0"
                            required
                            white
                        />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-4 mt-6">
                    <app-button
                        active
                        @click="$emit('update:open', false)"
                        :disabled="isLoading"
                    >
                        Отмена
                    </app-button>
                    <app-button
                        :active="formState.isValid"
                        :loading="isLoading"
                        @click="handleSave"
                    >
                        Сохранить
                    </app-button>
                </div>
            </div>
        </template>
    </UModal>
</template>

<script setup lang="ts">
import { RequiredPeriodsService } from "~/client";
import type { RequiredPeriod, CreateOrUpdatePeriodRequest } from "~/client";
import { ref, reactive, computed, watch, nextTick } from 'vue';

const props = defineProps<{
    period: RequiredPeriod | null;
    open: boolean;
}>();

const emit = defineEmits<{
    (e: "update:open", value: boolean): void;
    (e: "saved"): void;
}>();

const startDateInput = ref();
const endDateInput = ref();
const isLoading = ref(false);
const { $toast } = useNuxtApp();

// ===== FORM STATE =====
const form = reactive<CreateOrUpdatePeriodRequest>({
    period_start: '',
    period_end: '',
    photographers_count: 0,
    copywriters_count: 0,
    designers_count: 0,
});

const originalData = ref<RequiredPeriod | null>(null);

// ===== ВАЛИДАТОРЫ ДЛЯ КРАСНОЙ ПОДСВЕТКИ =====
const dateValidators = {
    start: (startValue: number | null) => {
        if (!form.period_start?.trim()) return false;
        if (!startValue) return false;
        const startDate = new Date(startValue);
        const endDate = form.period_end?.trim() ? new Date(form.period_end) : null;
        if (!endDate) return true;
        return startDate <= endDate;
    },
    end: (endValue: number | null) => {
        if (!form.period_end?.trim()) return false;
        if (!endValue) return false;
        const endDate = new Date(endValue);
        const startDate = form.period_start?.trim() ? new Date(form.period_start) : null;
        if (!startDate) return true;
        return endDate >= startDate;
    }
};

// ===== ОСНОВНОЙ COMPUTED ДЛЯ КНОПКИ =====
const formState = computed(() => {
    // 1. Все поля заполнены
    const isFilled = {
        period_start: !!form.period_start?.trim(),
        period_end: !!form.period_end?.trim(),
        photographers_count: form.photographers_count >= 0,
        copywriters_count: form.copywriters_count >= 0,
        designers_count: form.designers_count >= 0,
    };

    const allFilled = Object.values(isFilled).every(Boolean);

    // 2. Даты валидны
    const startValid = form.period_start?.trim()
        ? dateValidators.start(new Date(form.period_start).getTime())
        : false;
    const endValid = form.period_end?.trim()
        ? dateValidators.end(new Date(form.period_end).getTime())
        : false;

    // 3. Есть изменения (для редактирования)
    const hasChanges = computed(() => {
        if (!originalData.value) return true;
        return form.period_start.trim() !== originalData.value.period_start ||
               form.period_end.trim() !== originalData.value.period_end ||
               form.photographers_count !== (originalData.value.roles_config.find(r => r.user_role === 'photographer')?.count || 0) ||
               form.copywriters_count !== (originalData.value.roles_config.find(r => r.user_role === 'copywriter')?.count || 0) ||
               form.designers_count !== (originalData.value.roles_config.find(r => r.user_role === 'designer')?.count || 0);
    });

    return {
        isValid: allFilled && startValid && endValid && hasChanges.value,
        isFilled: allFilled,
        startValid,
        endValid,
        hasChanges: hasChanges.value,
        errors: {
            period_start: !isFilled.period_start || !startValid,
            period_end: !isFilled.period_end || !endValid,
        }
    };
});

// ===== EXPOSE ДЛЯ app-input =====
const validationState = computed(() => ({
    start: dateValidators.start,
    end: dateValidators.end
}));

// ===== ФУНКЦИИ =====
const resetForm = async (currentPeriod: RequiredPeriod | null) => {
    if (currentPeriod && props.open) {
        originalData.value = currentPeriod;
        form.period_start = currentPeriod.period_start;
        form.period_end = currentPeriod.period_end;
        form.photographers_count = currentPeriod.roles_config.find(r => r.user_role === 'photographer')?.count || 0;
        form.copywriters_count = currentPeriod.roles_config.find(r => r.user_role === 'copywriter')?.count || 0;
        form.designers_count = currentPeriod.roles_config.find(r => r.user_role === 'designer')?.count || 0;
    } else {
        originalData.value = null;
        Object.assign(form, {
            period_start: '',
            period_end: '',
            photographers_count: 0,
            copywriters_count: 0,
            designers_count: 0,
        });
    }
    // Ждем обновления DOM
    await nextTick();
    await updateEndDateMin();
};

const updateEndDateMin = async () => {
    if (form.period_start?.trim() && endDateInput.value) {
        await nextTick();
        const inputEl = (endDateInput.value as any)?.$el?.querySelector('input');
        if (inputEl) {
            inputEl.min = form.period_start;
            if (form.period_end && new Date(form.period_end) < new Date(form.period_start)) {
                form.period_end = form.period_start;
            }
        }
    }
};

const showDateErrorToast = () => {
    if (!formState.value.startValid || !formState.value.endValid) {
        $toast.error("Дата начала не может быть больше даты окончания");
    }
};

const handleSave = async () => {
    if (!formState.value.isValid) {
        $toast.error("Исправьте ошибки в форме перед сохранением");
        showDateErrorToast();
        return;
    }

    try {
        isLoading.value = true;

        if (props.period) {
            await RequiredPeriodsService.updateRequiredPeriodRequiredPeriodsPeriodIdPut(
                props.period.id,
                form
            );
            $toast.success("Период успешно обновлен");
        } else {
            await RequiredPeriodsService.createRequiredPeriodRequiredPeriodsPost(form);
            $toast.success("Период успешно создан");
        }

        emit("saved");
        emit("update:open", false);
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
};

// ===== WATCHERS =====
watch(() => props.open, async (newOpen) => {
    if (newOpen) {
        await resetForm(props.period);
    }
}, { immediate: true });

watch(() => form.period_start, async () => {
    await updateEndDateMin();
});

watch([() => form.period_start, () => form.period_end], () => {
    if (form.period_start?.trim() && form.period_end?.trim()) {
        if (!formState.value.startValid || !formState.value.endValid) {
            showDateErrorToast();
        }
    }
});
</script>
