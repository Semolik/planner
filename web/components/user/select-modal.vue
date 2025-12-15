<template>
    <UModal v-model:open="active" :title="title">
        <template #body>
            <div class="flex flex-col gap-2 min-h-[40vh]">
                <app-input
                    v-model="searchUsersQuery"
                    class="search-input"
                    placeholder="Поиск по пользователям"
                    type="text"
                />

                <!-- Прокручиваемый контейнер -->

                <div
                    ref="scrollContainer"
                    v-auto-animate
                    class="flex flex-col gap-2"
                    :style="{ 'max-height': '40vh', 'overflow-y': 'auto' }"
                >
                    <div
                        v-for="user in searchUsersResults"
                        :key="user.id"
                        class="user-item"
                        :class="{ excluded: user.excluded }"
                        @click="() => !user.excluded && emit('select', user)"
                    >
                        <div class="user-item-info">
                            <div class="name">
                                {{ useFullName(user) }}
                            </div>
                            <div
                                v-if="
                                    user.excluded && props.excludeUserBadgeText
                                "
                                class="badge"
                            >
                                {{ props.excludeUserBadgeText }}
                            </div>
                        </div>
                    </div>

                    <!-- Сообщение, если нет результатов -->
                    <div
                        v-if="searchUsersResults.length === 0 && !loading"
                        class="text-md text-gray-500 text-center"
                    >
                        Ничего не найдено
                    </div>

                    <!-- Лоадер подгрузки -->
                    <div
                        v-if="loading"
                        class="text-center py-2 text-sm text-gray-500"
                    >
                        Загрузка...
                    </div>
                </div>
            </div>
        </template>
    </UModal>
</template>
<script setup>
import { UsersService, UserRole } from "~/client";
import { useInfiniteScroll } from "@vueuse/core";

const props = defineProps({
    active: {
        type: Boolean,
        default: false,
    },
    filterRole: {
        type: String,
        default: null,
    },
    excludeUsers: {
        type: Array,
        default: () => [],
    },
    excludeUserBadgeText: {
        type: String,
    },
});

const { excludeUsers } = toRefs(props);

const title = computed(() => {
    if (!props.filterRole) return `Выбрать пользователя`;
    switch (props.filterRole) {
        case UserRole.COPYWRITER:
            return `Выбрать копирайтера`;
        case UserRole.PHOTOGRAPHER:
            return `Выбрать фотографа`;
        case UserRole.DESIGNER:
            return `Выбрать дизайнера`;
        default:
            return `Выбрать пользователя`;
    }
});

const emit = defineEmits(["update:active", "select"]);
const active = computed({
    get: () => props.active,
    set: (value) => emit("update:active", value),
});

const searchUsersQuery = ref("");
const excludeUsersIds = computed(() =>
    excludeUsers.value.map((user) => user.id)
);

// Состояние пагинации
const page = ref(1);
const hasMore = ref(true);
const loading = ref(false);
const allUsers = ref([]);

// Ссылка на контейнер прокрутки
const scrollContainer = ref(null);

// Загрузка пользователей
const loadUsers = async () => {
    if (loading.value || !hasMore.value) return;

    try {
        const response = await UsersService.getUsersUsersGet(
            searchUsersQuery.value,
            page.value,
            "last_name",
            "asc",
            false,
            false,
            props.filterRole
        );

        if (response.length === 0) {
            hasMore.value = false;
        } else {
            allUsers.value.push(...response);
            page.value++;
        }
    } catch (error) {
        console.error("Failed to load users:", error);
        hasMore.value = false;
    } finally {
        loading.value = false;
    }
};

watch([searchUsersQuery, () => props.filterRole], () => {
    allUsers.value = [];
    page.value = 1;
    hasMore.value = true;
    loadUsers();
});

watch(
    () => active,
    () => {
        if (!active.value) return;
        nextTick(() => {
            useInfiniteScroll(scrollContainer.value, () => loadUsers(), {
                canLoadMore: () => hasMore.value,
                distance: 10,
            });
        });
    },
    { immediate: true }
);

const searchUsersResults = computed(() =>
    allUsers.value.map((user) => ({
        ...user,
        excluded: excludeUsersIds.value.includes(user.id),
    }))
);
</script>
<style scoped lang="scss">
.user-list-container {
    border-top: 1px solid #eee;
    margin-top: 8px;
}

.user-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid $tertiary-bg;
    cursor: pointer;
    transition: border-color 0.2s;

    &:hover:not(.excluded) {
        border-color: $text-color;
    }

    &.excluded {
        cursor: not-allowed;
        opacity: 0.7;
    }

    .user-item-info {
        display: flex;
        justify-content: space-between;
        width: 100%;
        gap: 5px;
        min-width: 0;

        .name {
            font-size: 16px;
            color: $text-color-secondary;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 180px;
        }

        .badge {
            font-size: 14px;
            color: white;
            background-color: black;
            padding: 2px 5px;
            border-radius: 5px;
            display: inline-block;
        }
    }
}
</style>
