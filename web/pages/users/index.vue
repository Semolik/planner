<script setup lang="ts">
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

// Цвета для ролей
const roleColors: Record<UserRole, string> = {
    [UserRole.PHOTOGRAPHER]: "amber",
    [UserRole.COPYWRITER]: "blue",
    [UserRole.DESIGNER]: "rose",
};
const deleteUser = async () => {
    if (!selectedUser.value) return;

    try {
        await UsersService.deleteUserUsersUserIdDelete(selectedUser.value.id);

        $toast.success("Пользователь успешно удален");
        deleteUserModalOpen.value = false;
        selectedUser.value = null;
        reloadUsers();
    } catch (error) {
        $toast.error(HandleOpenApiError(error).message);
    }
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

            if (roles.length === 0) {
                return h(
                    UBadge,
                    {
                        color: "gray",
                        variant: "subtle",
                    },
                    () => "Нет ролей"
                );
            }

            return h(
                "div",
                { class: "flex flex-wrap gap-1" },
                roles.map((role) =>
                    h(
                        UBadge,
                        {
                            key: role,
                            color: roleColors[role] || "gray",
                            variant: "soft",
                            class: "capitalize",
                        },
                        () => role.replace("_", " ").toLowerCase()
                    )
                )
            );
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
        cell: ({ row }) => {
            return h("div", { class: "text-right flex gap-1 justify-end" }, [
                h(UButton, {
                    color: "neutral",
                    variant: "ghost",
                    icon: "material-symbols:edit-outline",
                    "aria-label": "Редактировать",
                    onClick: () => {
                        navigateTo(`/users/${row.original.id}`);
                    },
                }),
                h(UButton, {
                    color: "neutral",
                    variant: "ghost",
                    icon: "material-symbols:delete-outline",
                    "aria-label": "Удалить",
                    onClick: async () => {
                        selectedUser.value = row.original;
                        deleteUserModalOpen.value = true;
                    },
                }),
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
            <app-button active class="!min-h-0 ml-auto">
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
    <UModal
        v-model:open="deleteUserModalOpen"
        v-if="selectedUser"
        title="Удаление пользователя"
    >
        <template #body>
            <p>
                Вы уверены, что хотите удалить пользователя
                <strong>{{ useFullName(selectedUser) }} </strong>? Это действие
                нельзя будет отменить.
            </p>
            <div class="grid grid-cols-2 gap-2 mt-4">
                <app-button active @click="deleteUserModalOpen = false">
                    Отмена
                </app-button>
                <app-button active red @click="deleteUser">
                    Удалить
                </app-button>
            </div>
        </template>
    </UModal>
</template>
<style scoped lang="scss">
.head {
    border-bottom: 1px solid $border-color;
}
</style>
