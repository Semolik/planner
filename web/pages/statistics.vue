<script setup>
import { StatisticsService } from "@/client";

const UButton = resolveComponent("UButton");

const periodStart = ref("");
const periodEnd = ref("");

const setDefaultPeriod = () => {
    const now = new Date();
    const year = now.getFullYear();

    periodStart.value = `${year}-01-01`;

    periodEnd.value = `${year}-07-01`;
};

setDefaultPeriod();

const rawData = ref([]);
const loading = ref(false);

const loadData = async () => {
    loading.value = true;
    try {
        const data = await StatisticsService.getStatisticsStatisticsGet(
            periodStart.value,
            periodEnd.value
        );

        rawData.value = data;
    } catch (error) {
        console.error("Ошибка при загрузке статистики:", error);
    } finally {
        loading.value = false;
    }
};

watch([periodStart, periodEnd], loadData, { immediate: true });

const monthNames = [
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
];

const allMonths = computed(() => {
    return [
        ...new Set(rawData.value.flatMap((u) => Object.keys(u.stats || {}))),
    ].sort();
});

const sortField = ref("fullName");
const sortDirection = ref("asc");
const tableData = computed(() => {
    let data = rawData.value.map((user) => {
        const row = {
            fullName: `${user.user.last_name} ${user.user.first_name}`,
            lastName: user.user.last_name,
        };
        let total = 0;
        allMonths.value.forEach(function (month) {
            const value = user.stats?.[month] ?? 0;
            row[`month_${month}`] = value === 0 ? "-" : value;
            total += value;
        });
        row.total = total;
        return row;
    });

    if (sortField.value) {
        data.sort((a, b) => {
            const aValue = a[sortField.value];
            const bValue = b[sortField.value];
            if (aValue < bValue) return sortDirection.value === "asc" ? -1 : 1;
            if (aValue > bValue) return sortDirection.value === "asc" ? 1 : -1;
            return 0;
        });
    }

    return data;
});

const createSortableHeader = (title, field) => {
    return ({ column }) => {
        const isActive = sortField.value === field;
        const isAsc = sortDirection.value === "asc";
        return h(UButton, {
            color: "neutral",
            variant: "ghost",
            label: title,
            icon: isActive
                ? isAsc
                    ? "material-symbols:arrow-upward"
                    : "material-symbols:arrow-downward"
                : "material-symbols:swap-vert",
            class: "-mx-2.5",
            onClick: () => {
                if (sortField.value === field) {
                    sortDirection.value =
                        sortDirection.value === "asc" ? "desc" : "asc";
                } else {
                    sortField.value = field;
                    sortDirection.value = "asc";
                }
            },
        });
    };
};

const columns = computed(() => {
    return [
        {
            accessorKey: "fullName",
            header: createSortableHeader("ФИО", "fullName"),
        },
        ...allMonths.value.map((month) => ({
            accessorKey: `month_${month}`,
            header: monthNames[parseInt(month) - 1],
            align: "center",
        })),
        {
            accessorKey: "total",
            header: createSortableHeader("Итого", "total"),
            align: "center",
        },
    ];
});
</script>

<template>
    <div class="flex gap-2 max-w-2xl">
        <app-input v-model="periodStart" type="date" label="Начало периода" />
        <app-input v-model="periodEnd" type="date" label="Конец периода" />
    </div>

    <UTable :data="tableData" :columns="columns" v-if="!loading" />
    <p v-else>Загрузка данных...</p>
</template>
