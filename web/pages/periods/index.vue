<template>
    <page-container header="Отчетные периоды">
        <div class="flex-1 md:divide-accented w-full">
            <div
                class="flex md:items-center gap-2 min-h-[60px] overflow-x-auto px-2 head md:flex-row flex-col-reverse justify-between"
            >
                <div class="text-lg font-semibold">Отчетные периоды</div>
                <app-button
                    active
                    mini
                    @click="createPeriodModalOpen = true"
                    v-if="authStore.isAdmin"
                >
                    Создать период
                </app-button>
            </div>

            <div ref="tableContainer" class="overflow-auto">
                <UTable
                    :data="filteredData"
                    :columns="columns"
                    :loading="isLoading"
                    sticky
                />
            </div>
        </div>

        <required-period-delete-modal
            v-model:open="deletePeriodModalOpen"
            :period="selectedPeriod"
            @deleted="loadPeriods"
        />

        <required-period-form-modal
            v-model:open="createPeriodModalOpen"
            :period="editingPeriod"
            @saved="loadPeriods"
        />
    </page-container>
</template>

<script setup lang="ts">
import { routesNames } from "@typed-router";
import { h, resolveComponent, ref, computed } from "vue";
import type { TableColumn } from "@nuxt/ui";
import { RequiredPeriodsService, type RequiredPeriod, UserRole } from "~/client";
import { useAuthStore } from "~/stores/auth";

definePageMeta({
    middleware: ["admin"],
    layout: "no-padding",
});

useSeoMeta({
    title: "Отчетные периоды",
});

const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");
const Icon = resolveComponent("Icon");

const { $toast } = useNuxtApp();
const authStore = useAuthStore();

const data = ref<RequiredPeriod[]>([]);
const isLoading = ref(false);
const tableContainer = ref<HTMLElement>();
const deletePeriodModalOpen = ref(false);
const selectedPeriod = ref<RequiredPeriod | null>(null);
const createPeriodModalOpen = ref(false);
const editingPeriod = ref<RequiredPeriod | null>(null);

const roleTranslations: Record<UserRole, string> = {
    [UserRole.PHOTOGRAPHER]: "Фотографы",
    [UserRole.COPYWRITER]: "Копирайтеры",
    [UserRole.DESIGNER]: "Дизайнеры",
};

const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return isNaN(date.getTime())
        ? "Не указана"
        : date.toLocaleDateString("ru-RU");
};

const columns: TableColumn<RequiredPeriod>[] = [
    {
        accessorKey: "period",
        header: "Период",
        cell: ({ row }) => {
            const start = formatDate(row.original.period_start);
            const end = formatDate(row.original.period_end);

            if (start === end) {
                return start;
            }
            return `${start} - ${end}`;
        },
    },
    {
        id: "minimum_tasks",
        header: "Минимум по задачам",
        cell: ({ row }) => {
            const roles = row.original.roles_config || [];

            if (roles.length === 0) {
                return h("span", { class: "text-gray-400" }, "Не указано");
            }

            return h(
                "div",
                { class: "flex flex-wrap gap-1" },
                roles.map((roleConfig) =>
                    h(
                        UBadge,
                        {
                            key: roleConfig.user_role,
                            class: "capitalize",
                            variant: "subtle",
                            color: "neutral",
                        },
                        () =>
                            `${roleTranslations[roleConfig.user_role] || roleConfig.user_role} ${roleConfig.count}`
                    )
                )
            );
        },
    },
   {
    id: "actions",
    enableHiding: false,
    header: "Действия",
    // Убираем text-right с заголовка
    cell: ({ row }) => {
        return h("div", { class: "text-right flex gap-1 justify-end" }, [
            h(
                "div",
                {
                    class: "flex w-9 h-9 items-center justify-center bg-black rounded-xl hover:bg-gray-800 transition-colors cursor-pointer",
                    onClick: () => {
                        editingPeriod.value = row.original;
                        createPeriodModalOpen.value = true;
                    },
                },
                [
                    h(Icon, {
                        name: "material-symbols:edit-outline",
                        class: "text-white",
                    }),
                ]
            ),
            h(
                "div",
                {
                    class: "flex w-9 h-9 items-center justify-center bg-red-600 rounded-xl hover:bg-red-700 transition-colors cursor-pointer",
                    onClick: () => {
                        selectedPeriod.value = row.original;
                        deletePeriodModalOpen.value = true;
                    },
                },
                [
                    h(Icon, {
                        name: "material-symbols:delete-outline",
                        class: "text-white",
                    }),
                ]
            ),
        ]);
    },
},

];

const filteredData = computed(() => data.value);

async function loadPeriods() {
    if (isLoading.value) return;

    try {
        isLoading.value = true;
        const periods = await RequiredPeriodsService.getRequiredPeriodsRequiredPeriodsGet();
        data.value = periods;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

onMounted(() => {
    loadPeriods();
});
</script>

<style scoped lang="scss">
.head {
    @include md {
        border-bottom: 1px solid $border-color;
    }
}
</style>
