<script setup lang="ts">
import { routesNames } from "@typed-router";
import { h, resolveComponent, ref } from "vue";
definePageMeta({
    middleware: ["admin"],
    layout: "no-padding",
});
import { useInfiniteScroll } from "@vueuse/core";
import type { TableColumn } from "@nuxt/ui";
import { UsersService, type UserReadWithEmail, UserRole } from "~/client";

const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");
const Icon = resolveComponent("Icon");
const UInput = resolveComponent("UInput");

const { $toast } = useNuxtApp();

const data = ref<UserReadWithEmail[]>([]);
const isLoading = ref(false);
const searchQuery = ref("");
const page = ref(1);
const hasMore = ref(true);
const tableContainer = ref<HTMLElement>();
const orderBy = ref<"last_name" | "birth_date">("last_name");
const order = ref<"asc" | "desc">("asc");
const deleteUserModalOpen = ref(false);
const selectedUser = ref<UserReadWithEmail | null>(null);

const roleTranslations: Record<UserRole, string> = {
    [UserRole.PHOTOGRAPHER]: "Фотограф",
    [UserRole.COPYWRITER]: "Копирайтер",
    [UserRole.DESIGNER]: "Дизайнер",
};

const columns: TableColumn<UserReadWithEmail>[] = [
    {
        accessorKey: "full_name",
        header: ({ column }) => {
            const isActive = orderBy.value === "last_name";
            const isAsc = order.value === "asc";

            return h(UButton, {
                color: "neutral",
                variant: "ghost",
                label: "ФИО",
                icon: isActive
                    ? isAsc
                        ? "material-symbols:arrow-upward"
                        : "material-symbols:arrow-downward"
                    : "material-symbols:swap-vert",
                class: "-mx-2.5",
                onClick: () => {
                    orderBy.value = "last_name";
                    order.value = order.value === "asc" ? "desc" : "asc";
                    reloadUsers();
                },
            });
        },
        cell: ({ row }) => {
            const { last_name, first_name, patronymic } = row.original;
            return `${last_name} ${first_name}${patronymic ? " " + patronymic : ""}`;
        },
    },
    {
        accessorKey: "group",
        header: "Группа",
    },
    {
        accessorKey: "institute",
        header: "Институт",
        cell: ({ row }) => row.original.institute.name,
    },
    {
        accessorKey: "birth_date",
        header: ({ column }) => {
            const isActive = orderBy.value === "birth_date";
            const isAsc = order.value === "asc";

            return h(UButton, {
                color: "neutral",
                variant: "ghost",
                label: "Дата рождения",
                icon: isActive
                    ? isAsc
                        ? "material-symbols:arrow-upward"
                        : "material-symbols:arrow-downward"
                    : "material-symbols:swap-vert",
                class: "-mx-2.5",
                onClick: () => {
                    orderBy.value = "birth_date";
                    order.value = order.value === "asc" ? "desc" : "asc";
                    reloadUsers();
                },
            });
        },
        cell: ({ row }) => {
            const date = row.original.birth_date;
            if (!date) return "Не указана";

            const parsedDate = new Date(date);
            return isNaN(parsedDate.getTime())
                ? "Не указана"
                : parsedDate.toLocaleDateString();
        },
    },
    {
        id: "roles",
        header: "Роли",
        cell: ({ row }) => {
            const roles = row.original.roles || [];

            return h("div", { class: "flex flex-wrap gap-1" }, [
                ...(row.original.is_superuser
                    ? [
                          h(
                              UBadge,
                              {
                                  key: "admin",
                                  class: "capitalize",
                                  variant: "subtle",
                                  color: "info",
                              },
                              () => "Администратор"
                          ),
                      ]
                    : []),
                ...roles.map((role) =>
                    h(
                        UBadge,
                        {
                            key: role,
                            class: "capitalize",
                            variant: "subtle",
                            color: "neutral",
                        },
                        () => roleTranslations[role] || role
                    )
                ),
            ]);
        },
    },
    {
        accessorKey: "is_active",
        header: "Статус",
        cell: ({ row }) => {
            return h(
                UBadge,
                {
                    class: "capitalize",
                    variant: "subtle",
                    color: row.original.is_active ? "success" : "error",
                },
                () => (row.original.is_active ? "Активен" : "Неактивен")
            );
        },
    },
    {
        id: "actions",
        enableHiding: false,
        header: "Действия",

        cell: ({ row }) => {
            return h("div", { class: "text-right flex gap-1 justify-end" }, [
                h(
                    "div",
                    {
                        class: "flex w-9 h-9 items-center justify-center bg-black rounded-xl hover:bg-gray-800 transition-colors cursor-pointer",
                        onClick: () => {
                            navigateTo(`/users/${row.original.id}`);
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
                            selectedUser.value = row.original;
                            deleteUserModalOpen.value = true;
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

async function loadUsers() {
    if (isLoading.value || !hasMore.value) return;

    try {
        isLoading.value = true;
        const users = await UsersService.getUsersUsersGet(
            searchQuery.value,
            page.value,
            orderBy.value,
            order.value,
            false, // superusersToTop
            false // onlySuperusers
        );

        if (users.length === 0) {
            hasMore.value = false;
            return;
        }

        data.value = [...data.value, ...users];
        page.value++;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

async function reloadUsers() {
    if (isLoading.value) return;

    try {
        isLoading.value = true;
        page.value = 1;
        hasMore.value = true;

        const users = await UsersService.getUsersUsersGet(
            searchQuery.value,
            page.value,
            orderBy.value,
            order.value,
            false, // superusersToTop
            false // onlySuperusers
        );

        data.value = users;
        page.value++;
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    } finally {
        isLoading.value = false;
    }
}

useInfiniteScroll(
    tableContainer,
    async () => {
        await loadUsers();
    },
    { distance: 10 }
);

// Дебаунс поиска
const debouncedSearch = useDebounceFn(() => {
    reloadUsers();
}, 500);

watch(searchQuery, debouncedSearch);

onMounted(() => {
    reloadUsers();
});
</script>

<template>
    <div class="flex-1 divide-accented w-full">
        <div
            class="flex items-center gap-2 min-h-[60px] overflow-x-auto px-2 head"
        >
            <UInput
                v-model="searchQuery"
                class="max-w-sm min-w-[12ch]"
                placeholder="Поиск по фамилии..."
                icon="material-symbols:search"
            />
            <app-button
                active
                mini
                class="ml-auto"
                :to="{ name: routesNames.usersAdd }"
            >
                Добавить пользователя
            </app-button>
        </div>

        <div ref="tableContainer" class="overflow-auto">
            <UTable
                :data="data"
                :columns="columns"
                :loading="isLoading"
                sticky
            />
        </div>
    </div>

    <user-delete-modal
        v-model:open="deleteUserModalOpen"
        :user="selectedUser"
        @deleted="reloadUsers"
    />
</template>
<style scoped lang="scss">
.head {
    border-bottom: 1px solid $border-color;
}
</style>
