<template>
    <UModal :title="title" v-model:open="active">
        <template #body>
            <div class="flex flex-col gap-2 min-h-[40vh]">
                <app-input
                    class="search-input"
                    v-model="searchUsersQuery"
                    placeholder="Поиск по пользователям"
                    type="text"
                />

                <div
                    :class="[
                        'flex flex-col gap-2',
                        { grow: searchUsersResults.length === 0 },
                    ]"
                    v-auto-animate
                >
                    <div
                        class="user-item"
                        :class="{ excluded: user.excluded }"
                        v-for="user in searchUsersResults"
                        :key="user.id"
                        @click="() => !user.excluded && emit('select', user)"
                    >
                        <div class="user-item-info">
                            <div class="name">
                                {{ useFullName(user) }}
                            </div>
                            <div
                                class="badge"
                                v-if="
                                    user.excluded && props.excludeUserBadgeText
                                "
                            >
                                {{ props.excludeUserBadgeText }}
                            </div>
                        </div>
                    </div>

                    <div
                        class="text-md text-gray-500 text-center grow flex items-center justify-center"
                        v-if="searchUsersResults.length === 0"
                    >
                        Ничего не найдено
                    </div>
                </div>
            </div>
        </template>
    </UModal>
</template>
<script setup>
import { UsersService, UserRole } from "~/client";
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
    if (!props.filterRole) {
        return `Выбрать пользователя`;
    }
    switch (props.filterRole) {
        case UserRole.COPYWRITER:
            return `Выбрать копирайтера`;
        case UserRole.PHOTOGRAPHER:
            return `Выбрать фотографа`;
        case UserRole.DESIGNER:
            return `Выбрать дизайнера`;
    }
});
const emit = defineEmits(["update:active", "select"]);
const active = computed({
    get: () => props.active,
    set: (value) => emit("update:active", value),
});
const searchUsersQuery = ref("");

watch(active, (value) => {
    if (value) {
        searchUsersQuery.value = "";
    }
});
const excludeUsersIds = computed(() => {
    return excludeUsers.value.map((user) => user.id);
});
const searchResults = ref([]);
watch(
    [searchUsersQuery, () => props.filterRole],
    async () => {
        searchResults.value = await UsersService.getUsersUsersGet(
            searchUsersQuery.value,
            1,
            "last_name",
            "asc",
            false,
            false,
            props.filterRole
        );
    },
    { immediate: true }
);
const searchUsersResults = computed(() =>
    searchResults.value.map((user) => ({
        ...user,
        excluded: excludeUsersIds.value.includes(user.id),
    }))
);
</script>
<style scoped lang="scss">
.user-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px;
    border-radius: 10px;
    border: 1px solid $tertiary-bg;

    cursor: pointer;
    &:hover {
        border-color: $text-color;
    }

    &.excluded {
        cursor: not-allowed;
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
            display: block;
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
