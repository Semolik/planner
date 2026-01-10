<script setup lang="ts">
import { ref, computed, onMounted, resolveComponent } from "vue";
import { useHead } from "#imports";
import { UsersService, type UserReadWithEmail, UserRole } from "~/client";
import { HandleOpenApiError } from "~/composables/handleErrors";

definePageMeta({
  middleware: ["admin"],
  layout: "no-padding",
});

useHead({ title: "Дни рождения" });

const UBadge = resolveComponent("UBadge");
const UCard = resolveComponent("UCard");
const UButton = resolveComponent("UButton");
const { $toast } = useNuxtApp();

const isLoading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const users = ref<UserReadWithEmail[]>([]);

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

const roleTranslations: Record<UserRole, string> = {
  [UserRole.PHOTOGRAPHER]: "Фотограф",
  [UserRole.COPYWRITER]: "Копирайтер",
  [UserRole.DESIGNER]: "Дизайнер",
  [UserRole.MANAGER]: "Руководитель",
};

const filteredUsers = computed(() =>
  users.value.filter((user) => {
    const hasManager = user.roles?.includes(UserRole.MANAGER);
    if (!user.is_active && !hasManager) return false;
    return true;
  })
);

const groupedByMonth = computed(() => {
  const groups: { name: string; nameGenitive: string; items: Array<{ user: UserReadWithEmail; day: number; date: Date }> }[] = monthNames.map((name, idx) => ({ name, nameGenitive: monthNamesGenitive[idx], items: [] }));
  const noDate: UserReadWithEmail[] = [];

  filteredUsers.value.forEach((user) => {
    const dateStr = user.birth_date;
    if (!dateStr) {
      noDate.push(user);
      return;
    }
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      noDate.push(user);
      return;
    }
    const month = date.getMonth();
    groups[month].items.push({ user, day: date.getDate(), date });
  });

  groups.forEach((g) => g.items.sort((a, b) => a.day - b.day || a.user.last_name.localeCompare(b.user.last_name)));

  return { groups, noDate };
});

async function loadAllUsers() {
  if (isLoading.value) return;
  try {
    isLoading.value = true;
    users.value = [];
    page.value = 1;
    hasMore.value = true;

    while (hasMore.value) {
      const batch = await UsersService.getUsersUsersGet(
        undefined,
        page.value,
        "birth_date",
        "asc",
        false,
        false
      );
      if (!batch.length) {
        hasMore.value = false;
        break;
      }
      users.value = [...users.value, ...batch];
      page.value++;
    }
  } catch (error) {
    $toast.error(HandleOpenApiError(error).message);
  } finally {
    isLoading.value = false;
  }
}


onMounted(() => {
  loadAllUsers();
});
</script>

<template>

  <div class="flex-1 w-full px-2 md:px-4 py-4 space-y-4">
    <div class="flex items-center gap-2 flex-wrap">
      <h1 class="text-2xl font-semibold"></h1>
          <div class="text-lg font-semibold">Дни рождения</div>
    </div>

    <div class="grid gap-3">
      <UCard v-for="month in groupedByMonth.groups" :key="month.name" class="shadow-sm">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">{{ month.name }}</span>
            <UBadge variant="subtle" color="neutral">{{ month.items.length }}</UBadge>
          </div>
        </template>

        <div v-if="month.items.length" class="space-y-2">
          <div v-for="item in month.items" :key="item.user.id" class="flex items-center justify-between rounded-lg border border-gray-200 dark:border-gray-800 px-3 py-2">
            <div class="flex flex-col">
              <div class="font-medium">{{ item.user.last_name }} {{ item.user.first_name }}<span v-if="item.user.patronymic"> {{ item.user.patronymic }}</span></div>
              <div class="text-sm text-gray-500 flex flex-wrap gap-2">

                <span v-if="item.user.roles?.length">{{ item.user.roles.map((r) => roleTranslations[r] || r).join(", ") }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
             <app-button mini active>
                 {{ item.day }} {{ month.nameGenitive }}
             </app-button>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-500">Нет дней рождения в этом месяце</div>
      </UCard>

      <UCard v-if="groupedByMonth.noDate.length" class="shadow-sm">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">Без даты рождения</span>
            <UBadge variant="subtle" color="neutral">{{ groupedByMonth.noDate.length }}</UBadge>
          </div>
        </template>
        <div class="space-y-2">
          <div v-for="user in groupedByMonth.noDate" :key="user.id" class="flex items-center justify-between rounded-lg border border-gray-200 dark:border-gray-800 px-3 py-2">
            <div class="flex flex-col">
              <div class="font-medium">{{ user.last_name }} {{ user.first_name }}<span v-if="user.patronymic"> {{ user.patronymic }}</span></div>
              <div class="text-sm text-gray-500 flex flex-wrap gap-2">

                <span v-if="user.roles?.length">• {{ user.roles.map((r) => roleTranslations[r] || r).join(", ") }}</span>
              </div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm text-gray-500">Дата не указана</span>
              <UButton color="neutral" variant="ghost" icon="material-symbols:open-in-new" :to="`/users/${user.id}`" />
            </div>
          </div>
        </div>
      </UCard>
    </div>
  </div>
</template>
