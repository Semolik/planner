<template>
  <page-container header="Статистика по периодам">
    <div class="flex-1 md:divide-accented w-full">
      <div class="flex md:items-center gap-2 min-h-[60px] overflow-x-auto px-2 head md:flex-row flex-col-reverse justify-between">
        <div class="text-lg font-semibold">Статистика</div>
      </div>

      <div class="space-y-4 p-4">
        <!-- Селектор периода -->
        <div class="flex gap-2 max-w-2xl flex-wrap">
          <app-button
            v-for="period in periods"
            :key="period.id"
            active
            :outline="!period.active"
            @click="selectedPeriod = period"
            class="flex-1 justify-between whitespace-nowrap min-w-[200px]"
          >
            <span class="text-sm">
              {{ formatPeriod(period) }}
            </span>
          </app-button>
        </div>

        <!-- Бейджи с минимальными требованиями -->
        <div v-if="formattedRequirements.length > 0" class="flex gap-2 flex-wrap items-center">
          <span class="text-sm text-gray-600 font-medium">Минимум задач:</span>
          <UBadge
            v-for="req in formattedRequirements"
            :key="req.role"
            color="neutral"
            size="md"
          >
            {{ req.label }}: {{ req.count }}
          </UBadge>
        </div>
      </div>

      <div ref="tableContainer" class="overflow-auto">
        <UTable
          v-if="!loading"
          :columns="columns"
          :data="tableData"
          :grouping="['user_id']"
          :grouping-options="groupingOptions"
          :ui="{
            root: 'min-w-full',
            td: 'empty:p-0'
          }"
          sticky
        >
          <!-- колонка ФИО / тип активности -->
          <template #title-cell="{ row }">
            <div v-if="row.getIsGrouped()" class="flex items-center">
              <UButton
                variant="ghost"
                color="neutral"
                class="mr-2"
                size="xs"
                :icon="row.getIsExpanded() ? 'i-lucide-chevron-down' : 'i-lucide-chevron-right'"
                @click="row.toggleExpanded()"
              />
              <strong>{{ row.original.fullName }}</strong>
            </div>
            <div v-else class="ml-8 text-gray-600">
              {{ activityTypeLabels[row.original.activityType] }}
            </div>
          </template>

          <!-- месяцы -->
          <template
            v-for="month in allMonths"
            :key="`month_${month}`"
            #[`month_${month}-cell`]="{ row }"
          >
            <div v-if="row.getIsGrouped()" class="text-center font-semibold">
              {{ row.getValue(`month_${month}`) === 0 ? '-' : row.getValue(`month_${month}`) }}
            </div>
            <div v-else class="text-center">
              {{ row.getValue(`month_${month}`) }}
            </div>
          </template>

          <!-- итоговая колонка -->
          <template #total-cell="{ row }">
            <!-- групповая строка пользователя -->
            <div
              v-if="row.getIsGrouped()"
              class="text-center font-semibold"
              :class="{
                'bg-red-100 text-red-700': hasAnyRoleDeficiencyForUser(row),
                'bg-green-100 text-green-700': !hasAnyRoleDeficiencyForUser(row) && row.getValue('total') > 0
              }"
            >
              {{ row.getValue('total') }}
            </div>

            <!-- строки по ролям (как раньше) -->
            <div
              v-else
              class="text-center font-semibold"
              :class="{
                'bg-red-100 text-red-700': !isTaskCountSufficient(row.original.activityType, row.getValue('total')),
                'bg-green-100 text-green-700': isTaskCountSufficient(row.original.activityType, row.getValue('total')) && row.getValue('total') > 0
              }"
            >
              {{ row.getValue('total') }}
            </div>
          </template>
        </UTable>

        <div v-else class="flex justify-center items-center py-12">
          <p class="text-gray-500">Загрузка данных...</p>
        </div>
      </div>
    </div>
  </page-container>
</template>

<script setup lang="ts">
import { StatisticsService, RequiredPeriodsService } from "@/client";
import { resolveComponent, ref, computed, watch } from "vue";
import { getGroupedRowModel } from "@tanstack/vue-table";

definePageMeta({
  middleware: ["admin"],
  layout: "no-padding",
});

useSeoMeta({
  title: "Статистика по периодам",
});

const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");

const periodsRaw = await RequiredPeriodsService.getRequiredPeriodsRequiredPeriodsGet();
const selectedPeriod = ref(periodsRaw[0]);
const periods = computed(() =>
  periodsRaw.map((p) => ({
    ...p,
    active: selectedPeriod.value && p.id === selectedPeriod.value.id,
  })),
);

const rawData = ref<any[]>([]);
const loading = ref(false);
const tableContainer = ref<HTMLElement | null>(null);

const loadData = async () => {
  if (!selectedPeriod.value) {
    rawData.value = [];
    return;
  }
  loading.value = true;
  try {
    const data = await StatisticsService.getStatisticsStatisticsGet(
      selectedPeriod.value.id,
    );
    rawData.value = data;
  } catch (error) {
    console.error("Ошибка при загрузке статистики:", error);
  } finally {
    loading.value = false;
  }
};

watch(selectedPeriod, loadData, { immediate: true });

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

const monthNamesGenitive = [
  "января",
  "февраля",
  "марта",
  "апреля",
  "мая",
  "июня",
  "июля",
  "августа",
  "сентября",
  "октября",
  "ноября",
  "декабря",
];

const formatDate = (isoDate: string, showYear = false): string => {
  if (!isoDate) return "";
  const parts = String(isoDate).split("-");
  if (parts.length !== 3) return isoDate;
  const [year, month, day] = parts;
  const m = parseInt(month, 10) - 1;
  const dd = String(parseInt(day, 10));
  const monthName = monthNamesGenitive[m] || monthNames[m] || month;
  return showYear ? `${dd} ${monthName} ${year}` : `${dd} ${monthName}`;
};

const formatPeriod = (period: any): string => {
  const start = period.period_start;
  const end = period.period_end;
  const startYear = start ? String(start).split("-")[0] : null;
  const endYear = end ? String(end).split("-")[0] : null;
  const currentYear = String(new Date().getFullYear());
  const showYear =
    startYear !== endYear ||
    startYear !== currentYear ||
    endYear !== currentYear;
  return `${formatDate(start, showYear)} - ${formatDate(end, showYear)}`;
};

const allMonths = computed(() => {
  return [
    ...new Set(
      rawData.value.flatMap((u: any) => Object.keys(u.stats || {})),
    ),
  ].sort((a: string, b: string) => parseInt(a) - parseInt(b));
});

const requiredTasksMap = computed(() => {
  if (!selectedPeriod.value?.roles_config) return {};
  const map: Record<string, number> = {};
  selectedPeriod.value.roles_config.forEach((config: any) => {
    map[config.user_role] = config.count;
  });
  return map;
});

const formattedRequirements = computed(() => {
  if (!selectedPeriod.value?.roles_config) return [];

  const roleLabels: Record<string, string> = {
    photographer: "Фотограф",
    copywriter: "Копирайтер",
    designer: "Дизайнер",
  };

  return selectedPeriod.value.roles_config.map((config: any) => ({
    label: roleLabels[config.user_role] || config.user_role,
    count: config.count,
    role: config.user_role,
  }));
});

const tableData = computed(() => {
  const data: any[] = [];

  rawData.value.forEach((user: any) => {
    const userId = user.user.id;
    const fullName = `${user.user.last_name} ${user.user.first_name}`;

    ["photographer", "copywriter", "designer"].forEach((activityType) => {
      const row: any = {
        id: `${userId}_${activityType}`,
        user_id: userId,
        fullName: fullName,
        activityType: activityType,
      };

      allMonths.value.forEach((month) => {
        const value = user.stats?.[month]?.[activityType] || 0;
        row[`month_${month}`] = value === 0 ? "-" : value;
      });

      row.total = allMonths.value.reduce((sum: number, month: string) => {
        const val = row[`month_${month}`];
        return sum + (val === "-" ? 0 : val);
      }, 0);

      data.push(row);
    });
  });

  return data;
});

const activityTypeLabels: Record<string, string> = {
  photographer: "Фотограф",
  copywriter: "Копирайтер",
  designer: "Дизайнер",
};

const isTaskCountSufficient = (activityType: string, total: number): boolean => {
  const required = requiredTasksMap.value[activityType] || 0;
  return total >= required;
};

/**
 * Проверка: есть ли у пользователя хоть одна роль,
 * у которой total < required.
 * Вызывается только для групповой строки пользователя.
 */
const hasAnyRoleDeficiencyForUser = (groupRow: any): boolean => {
  const userId = groupRow.original.user_id;
  const userRows = tableData.value.filter((r) => r.user_id === userId);

  return userRows.some((userRow) => {
    const total = userRow.total;
    const activityType = userRow.activityType;
    return !isTaskCountSufficient(activityType, total);
  });
};

const columns = computed(() => {
  return [
    {
      id: "title",
      header: "ФИО / Тип активности",
    },
    {
      id: "user_id",
      accessorKey: "user_id",
    },
    ...allMonths.value.map((month: string) => ({
      accessorKey: `month_${month}`,
      header: monthNames[parseInt(month) - 1],
      cell: ({ row }: any) => {
        if (row.getIsGrouped()) {
          return "";
        }
        return row.getValue(`month_${month}`);
      },
      aggregatedCell: ({ getValue }: any) => {
        const value = getValue();
        return value === 0 || value === "-" ? "-" : value;
      },
      aggregationFn: (columnId: string, leafRows: any[]) => {
        const sum = leafRows.reduce((total: number, row: any) => {
          const val = row.getValue(columnId);
          return total + (val === "-" ? 0 : parseInt(val) || 0);
        }, 0);
        return sum;
      },
      meta: {
        class: {
          th: "text-center",
          td: "text-center",
        },
      },
    })),
    {
      accessorKey: "total",
      header: "Итого",
      cell: ({ row }: any) => {
        if (row.getIsGrouped()) {
          return "";
        }
        return row.getValue("total");
      },
      aggregatedCell: ({ getValue }: any) => {
        return getValue();
      },
      aggregationFn: "sum",
      meta: {
        class: {
          th: "text-center",
          td: "text-center font-semibold",
        },
      },
    },
  ];
});

const groupingOptions = ref({
  groupedColumnMode: "remove",
  getGroupedRowModel: getGroupedRowModel(),
});
</script>

<style scoped lang="scss">
.head {
  @include md {
    border-bottom: 1px solid $border-color;
  }
}
</style>
